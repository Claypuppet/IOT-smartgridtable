/*
 * Smart Grid TableController handles messages received by Smart Grid MainController
 * It displays a simulation of the electrical grid between consumers and producers  
 * 
 * The TableController sends messages to the MainController when a module/other table is placed.
 * The MainController receives these messages and does the calculation of the simulation. 
 * When the calculation is done, the MainController sends the grid/flow configuration back and the TableController shows the simulation
 * 
 * For configurations see config.h
 * 
 * Created by: Joris van Zeeland, Jelle Bouwhuis, Kevin Taartmans, Sam Teuwsen, Willem van der Krol, Derk Wiegerinck
 * Contact: jorisvanzeeland@hotmail.com
 * Date: July 11th, 2017
 * Commisioned by: Dr. Ballard Asare-Bediako, Dhr. Eddy Luursema 
 * Location: HAN University of Applied Sciences - Arnhem
 */

#include "config.h"

#include <MySensors.h>
#include <SPI.h>
#include <Wire.h>

#include "ledstrip.h"
#include "grid.h"
#include "protocol.h"
#include "rfid.h"
#include "ring-buffer.h"
#include "synced-millis.h"

// Buffer for RFID message received by I2C
volatile RingBuffer RFID_msg_buf = ring_create();

//present tablesection to maincontroller
void presentation() {
  present(TABLE_SECTION_ID, S_CUSTOM);
}

void setup()
{
  /* start I2C as slave */
  Wire.begin(SLAVE_ID);
  Wire.onReceive(i2c_receive);

  // start SPI for RFID readers and NRF24
  SPI.begin();

  // initialize RFID readers 
  for (size_t i = 0; i < RFID_COUNT; i++)
  {
    RFID_init(&RFIDs[i]);
  }

  // initialize led strips
  ledstrip_setup();

  //Set RST pin on helper high default status
  pinMode(A3, OUTPUT);
  digitalWrite(A3, LOW);
  delay(5);
  digitalWrite(A3, HIGH);

} // End setup()

void loop()
{
  // Holds value at which millis to check the RFIDs again
  static uint32_t next_RFID_check = 0;
  // Holds value of which RFID reader to check next
  static uint8_t next_RFID = 0;

  // Stores current millis for later use
  uint32_t now = millis();

  // Check next RFID after RFID_CHECK_DELAY (set in config.h)
  if (now > next_RFID_check)
  {
    next_RFID_check = now + RFID_CHECK_DELAY;

    // handle an RFID on this Arduino
    handle_RFID(&RFIDs[next_RFID], next_RFID);

    next_RFID = (next_RFID + 1) % RFID_COUNT;
  }

  // handle an RFID message received by I2C
  if (ring_length(&RFID_msg_buf) > 0)
  {
    // Disable interrupts to get the RFID message from the buffer, then enable interrupts again.
    noInterrupts();
    RFID_message RFID_msg = ring_pop(&RFID_msg_buf);
    interrupts();

    handle_RFID_message(&RFID_msg);
  }
  ledstrip_update();
} // End loop()

// Handles incoming message from main-controller. This is a built-in function from the MySensors library
void receive(const MyMessage &msg)
{
  // if TEST_MODULE is placed don't receive messages
  if (ledstrip_test(testReady)) {
    return;
  }

  // Check if it needs a reboot
  if (msg.type == REBOOT_BOSS_AND_HELPER_MSG) {
    Serial.println("Reboot command received from maincontroller");
    reboot_boss_and_helper();
  }

  // Check if there is an update for the flow_segment configuration
  if (msg.type == FLOW_CONFIG_CHANGE_MSG)
  {
    Grid grid = grid_from_parsed_grid(msg.getCustom());

    ledstrip_set_grid(&grid);

    // Force led strip update
    ledstrip_update(true);

#ifdef MY_DEBUG
    // If debugging is enabled, this will print the energy grid (grid) info
    grid_print(&grid);
#endif

  }
  // Check if there is a color change message 
  else if (msg.type == COLOR_CHANGE_MSG)
  {
    // convert string to RGB value
     char rgbHex[7];
    msg.getString(rgbHex);
    rgbHex[6] = '\0';

    uint32_t rgb = strtoul(rgbHex, NULL, 16);

    ledstrip_set_color(msg.sensor, rgb);

    // force led strip update
    ledstrip_update(true);
  }
  // Check if there is a time synchronization message (for cross-table segments flow_segment synchronization)
  else if (msg.type == TIME_SYNC_MSG)
  {
    set_millis(msg.getULong());
  }


} // End receive()

// Handles RFID tag detection from boss
void handle_RFID(RFID *RFID, uint8_t sensor_id)
{
  // Jump out of the function if the RFID state has not changed
  if (!RFID_state_changed(RFID))
  {
    return;
  }

  // create RFID message
  RFID_message msg = {
    .sensor_id = sensor_id,
    .tag_present = RFID->tag_present,
  };

  // read tag ID if a tag is present
  if (msg.tag_present)
  {
    bool tag_id_read = RFID_start_auth(RFID) &&
                       RFID_tag_read_id(RFID, &msg);

    RFID_stop_auth(RFID);
        
    // Jump out of the function if the tag can't be read properly
    if (!tag_id_read)
    {
      return;
    }
  }
  handle_RFID_message(&msg);
} // End handle_RFID()

// Processes the incoming RFID message
void handle_RFID_message(const RFID_message *msg)
{


#ifdef MY_DEBUG
  // If debugging is enabled, this prints the RFID message
  RFID_message_print(msg);
#endif

  // report change to main controller
  const SensorInfo *sensor = &sensor_info[msg->sensor_id];

  if (sensor->type == MODULE_SENSOR)
  {
    uint32_t module_id = msg->tag_present ? msg->tag_id : 0;

    change_module(sensor->location, module_id);
  }
  else // If the sensor type is not a module sensor, it must be a table detection sensor
  {
    uint32_t table_section_id = msg->tag_present ? msg->tag_id : 0;

    change_neighbor(sensor->location, table_section_id);
  }

   // if TEST_MODULE is placed execute ledstrip_test
    if (msg->tag_id == TEST_MODULE_ID && msg->tag_present == true)
    {
      Serial.println("Test module is placed");
      testReady = false;
      testReady = ledstrip_test(testReady);
    }
} // End handle_RFID_message()

// Receives RFID messages from helper by I2C
// Interrupt routine fills RFID message per byte with a 6 byte large ring buffer
void i2c_receive(int bytes)
{
  RFID_message RFID_msg;

  // Read from i2c
  uint8_t *buf = (uint8_t *) &RFID_msg;
  for (size_t i = 0; i < sizeof RFID_msg; i++)
  {
    buf[i] = Wire.read();
  }

  // Update sensor ID
  RFID_msg.sensor_id += RFID_COUNT;

  // Add message to the ring buffer
  ring_push(&RFID_msg_buf, RFID_msg);
} // End i2c_receive()

void reboot_boss_and_helper() {
  Serial.println("rebooting system");
  //wait for it to reboot

  //reboot sketch on boss for soft reset
  asm volatile ("  jmp 0");
} 

