/**
    MySensors GatewaySerial sketch, edited to imitate a main controller for the Smart Grid Table.
*/

// Enable debug prints to serial monitor
// #define MY_DEBUG

#define MY_RADIO_NRF24
#define MY_RF24_CHANNEL 93
#define MY_RF24_PA_LEVEL RF24_PA_LOW

// Enable serial gateway
#define MY_GATEWAY_SERIAL

#include <MySensors.h>

char received_data;
boolean new_data = false;

void setup()
{
  MyMessage rebootmsg(0,  V_VAR1);
  rebootmsg.setDestination(255); /* Broadcast to all connected table parts */
  send(rebootmsg);

  Serial.println("Smart grid table - Gateway Emulator");
  Serial.println("");
  Serial.println("Available tests:");
#ifdef MY_DEBUG
  Serial.println("r - reboot all connected tables (DEBUG PURPOSES ONLY)");
#endif
  Serial.println("o - turn all the leds off");
  Serial.println("1 - turn all the leds to high voltage, overloaded, high speed, reversed");
  Serial.println("2 - turn all the leds to low voltage, normal load, low speed, not reversed");
  Serial.println("3 - turn only the ring on, with low voltage, normal load, low speed, not reversed");
}

void presentation()
{
}

void loop()
{
  listen_for_serial_input();
  send_message();
}

void send_message()
{
  if (new_data == true)
  {
#ifdef MY_DEBUG
    if (received_data == 'r')
    {
      MyMessage msg(0,  V_VAR1);
      msg.setDestination(255);
      send(msg);
    }
    else
#endif
      if (received_data == 'o')
      {
        MyMessage msg(0,  V_VAR4);
        msg.setDestination(255);
        char value[] = {0b00000000,   /* Network header */
                        0b00000000,   /* Section 1 */
                        0b00000000,   /* Section 2 */
                        0b00000000,   /* Section 3 */
                        0b00000000,   /* Section 4 */
                        0b00000000,   /* Section 5 */
                        0b00000000,   /* Section 6 */
                        0b00000000,   /* Section 7 */
                        0b00000000,   /* Section 8 */
                        0b00000000,   /* Section 9 */
                        0b00000000,   /* Section 10 */
                        0b00000000,   /* Section 11 */
                        0b00000000,   /* Section 12 */
                        0b00000000,   /* Section 13 */
                        0b00000000,   /* Section 14 */
                        0b00000000,   /* Section 15 */
                        0b00000000,   /* Section 16 */
                        0b00000000,   /* Section 17 */
                        0b00000000,   /* Section 18 */
                        0b00000000,   /* Section 19 */
                        0b00000000    /* Section 20 */
                       };
        send(msg.set(value, 21));
      }
      else if (received_data == '1')
      {
        MyMessage msg(0,  V_VAR4);
        msg.setDestination(255);
        char value[] = {0b10000000,   /* Network header */
                        0b01111011,   /* Section 1 */
                        0b01111011,   /* Section 2 */
                        0b01111011,   /* Section 3 */
                        0b01111011,   /* Section 4 */
                        0b01111011,   /* Section 5 */
                        0b01111011,   /* Section 6 */
                        0b01111011,   /* Section 7 */
                        0b01111011,   /* Section 8 */
                        0b01111011,   /* Section 9 */
                        0b01111011,   /* Section 10 */
                        0b01111011,   /* Section 11 */
                        0b01111011,   /* Section 12 */
                        0b01111011,   /* Section 13 */
                        0b01111011,   /* Section 14 */
                        0b01111011,   /* Section 15 */
                        0b01111011,   /* Section 16 */
                        0b01111011,   /* Section 17 */
                        0b01111011,   /* Section 18 */
                        0b01111011,   /* Section 19 */
                        0b01111011    /* Section 20 */
                       };
        send(msg.set(value, 21)); /* 21 is the size of the message buffer: 1 network header + 20 sections (1 byte per section) */
      }
      else if (received_data == '2')
      {
        MyMessage msg(0,  V_VAR4);
        msg.setDestination(255);
        char value[] = {0b00000000,   /* Network header */
                        0b00000011,   /* Section 1 */
                        0b00000011,   /* Section 2 */
                        0b00000011,   /* Section 3 */
                        0b00000011,   /* Section 4 */
                        0b00000011,   /* Section 5 */
                        0b00000011,   /* Section 6 */
                        0b00000011,   /* Section 7 */
                        0b00000011,   /* Section 8 */
                        0b00000011,   /* Section 9 */
                        0b00000011,   /* Section 10 */
                        0b00000011,   /* Section 11 */
                        0b00000011,   /* Section 12 */
                        0b00000011,   /* Section 13 */
                        0b00000011,   /* Section 14 */
                        0b00000011,   /* Section 15 */
                        0b00000011,   /* Section 16 */
                        0b00000011,   /* Section 17 */
                        0b00000011,   /* Section 18 */
                        0b00000011,   /* Section 19 */
                        0b00000011    /* Section 20 */
                       };
        send(msg.set(value, 21)); /* 21 is the size of the message buffer: 1 network header + 20 sections (1 byte per section) */
      }
      else if (received_data == '3')
      {
        MyMessage msg(0,  V_VAR4);
        msg.setDestination(255);
        char value[] = {0b00000000,   /* Network header */
                        0b00000000,   /* Section 1 */
                        0b00000000,   /* Section 2 */
                        0b00000000,   /* Section 3 */
                        0b00000011,   /* Section 4 */
                        0b00000000,   /* Section 5 */
                        0b00000000,   /* Section 6 */
                        0b00000011,   /* Section 7 */
                        0b00000000,   /* Section 8 */
                        0b00000000,   /* Section 9 */
                        0b00000011,   /* Section 10 */
                        0b00000000,   /* Section 11 */
                        0b00000000,   /* Section 12 */
                        0b00000000,   /* Section 13 */
                        0b00000011,   /* Section 14 */
                        0b00000000,   /* Section 15 */
                        0b00000000,   /* Section 16 */
                        0b00000011,   /* Section 17 */
                        0b00000000,   /* Section 18 */
                        0b00000000,   /* Section 19 */
                        0b00000011    /* Section 20 */
                       };
        send(msg.set(value, 21)); /* 21 is the size of the message buffer: 1 network header + 20 sections (1 byte per section) */
      }
  }
  new_data = false;
}

byte flipByte(byte c)
{
  char r = 0;
  for (byte i = 0; i < 8; i++) {
    r <<= 1;
    r |= c & 1;
    c >>= 1;
  }
  return r;
}

void listen_for_serial_input()
{
  if (Serial.available() > 0)
  {
    received_data = Serial.read();
    new_data = true;
  }
}

void receive(const MyMessage &msg)
{
  char s[10];
  msg.getString(s);
  if (msg.type == V_VAR2)
  {
    Serial.print("Table ID: ");
    Serial.println(msg.sender);
    Serial.print("RFID Reader: ");
    Serial.println(msg.sensor);
    if (s[0] != '0')
    {
      Serial.print("Module placed with UID ");
      Serial.println(s);
    }
    else
    {
      Serial.println("Module removed");
    }
  }
}

