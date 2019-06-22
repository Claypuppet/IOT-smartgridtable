#include "config.h"
#include "load.h"
#include "voltage.h"

/* CURRENT TABLE RFID SETUP (AS SEEN FROM THE FRONT OF THE TABLE)
 * ************************************************************************************
 *        NORTH SIDE              
 *        
 *            T0                                          D8 
 *        M1       M2                                 D5       D7  
 *           \|_|/                                       \|_|/
 *      M0___/   \___3M              HELPER SIDE    D6___/   \___D6   BOSS SIDE
 *           \___/                                       \___/
 *           /| |\                                       /| |\
 *        M5       4M                                 D7       D5
 *            T1                                          D8
 *            
 *        SOUTH SIDE    
 * ************************************************************************************   
 * M0/5 = MODULE_SENSORS
 * T0/1 = TABLE_SECTION_SENSORS
 * 
 * I/O Arduino pinout boss (as seen from the front of the table):
 * 
 * M4 = D5 (boss)
 * M3 = D6 (boss)
 * M2 = D7 (boss)
 * T0 = D8 (boss)
 *
 * M1 = D5 (helper)
 * M0 = D6 (helper)
 * M5 = D7 (helper)
 * T1 = D8 (helper)
 */

// initialization of table sensors and locations on the table 
const SensorInfo sensor_info[] = {
  [0] = { .type = MODULE_SENSOR,     .location = 4 }, //boss --digitalpin 5 
  [1] = { .type = MODULE_SENSOR,     .location = 3 }, //boss --digitalpin 6
  [2] = { .type = MODULE_SENSOR,     .location = 2 }, //boss --digitalpin 7
  [3] = { .type = TABLE_SECTION_SENSOR, .location = 0 }, //boss --digitalpin 8
  [4] = { .type = MODULE_SENSOR,     .location = 1 }, //helper --digitalpin 5
  [5] = { .type = MODULE_SENSOR,     .location = 0 }, //helper --digitalpin 6
  [6] = { .type = MODULE_SENSOR,     .location = 5 }, //helper --digitalpin 7
  [7] = { .type = TABLE_SECTION_SENSOR, .location = 1 }, //helper --digitalpin 8
};

// initialization of RFID objects on the boss (helper RFIDs are send through I2C communication)
RFID RFIDs[RFID_COUNT] = {
  RFID_create(RFID0_SDA_PIN, RFID_RST_PIN),
  RFID_create(RFID1_SDA_PIN, RFID_RST_PIN),
  RFID_create(RFID2_SDA_PIN, RFID_RST_PIN),
  RFID_create(RFID3_SDA_PIN, RFID_RST_PIN),
};

// initialization of color settings with voltage being background color and load being foreground color
CRGB off_color = CRGB::Black;
CRGB error_color = CRGB::Red;
CRGB voltage_colors[] = {
  [VOLTAGE_LOW] = CRGB::Grey,
  [VOLTAGE_MEDIUM] = CRGB::DarkMagenta,
  [VOLTAGE_HIGH] = CRGB::DarkBlue,
};
CRGB load_colors[] = {
  [LOAD_NORMAL] = CRGB::Green,
  [LOAD_HIGH] = CRGB::Yellow,
  [LOAD_CRITICAL] = CRGB::Red,
};
