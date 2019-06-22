#ifndef CONFIG_H
#define CONFIG_H

#include <FastLED.h>

#include "rfid.h"
#include "sensor-info.h"

// Enable the MY_DEBUG define to show debug messages
#define MY_DEBUG

// MySensors radio defines
#define MY_RADIO_NRF24
#define MY_RF24_PA_LEVEL RF24_PA_HIGH
#define MY_NODE_ID TABLE_SECTION_ID

//set radio channel between 0-126
#define MY_RF24_CHANNEL 93

// Table section ID set node id between 1-254
#define TABLE_SECTION_ID 3

// ID of this I2C slave
#define SLAVE_ID 1

// Shared RFID reset pin
#define RFID_RST_PIN A0

// RFID data pins 
#define RFID0_SDA_PIN 5
#define RFID1_SDA_PIN 6
#define RFID2_SDA_PIN 7
#define RFID3_SDA_PIN 8

// Number of RFIDs on this Arduino
#define RFID_COUNT 4

// Delay in ms between RFID checks
#define RFID_CHECK_DELAY 75

// Led strip data pin
#define LEDSTRIP_DATA_PIN 3

// Led strip clock pin
#define LEDSTRIP_CLK_PIN 2

// Led strip type with clock pin (currently SK9822 is used, not APA102 even though it says on the label because of chinese clone manufacturers)
// if you do use APA102 make sure that they are not clones, because of the difference in CLOCK signals ------ you can add more types, see: https://github.com/FastLED/FastLED/wiki/Overview 
#define LEDSTRIP_TYPE SK9822
//#define LEDSTRIP_TYPE APA102
//#define LEDSTRIP_TYPE WS2801

// Led strip types without clock pin ---- you can add more types, see: https://github.com/FastLED/FastLED/wiki/Overview
//#define LEDSTRIP_TYPE_WITHOUT_CLOCK WS2812
//#define LEDSTRIP_TYPE_WITHOUT_CLOCK WS2812B
//#define LEDSTRIP_TYPE_WITHOUT_CLOCK WS2811
//#define LEDSTRIP_TYPE_WITHOUT_CLOCK NEOPIXEL

// Number of flow_segments
#define FLOW_SEGMENT_COUNT 20

// Number of LEDs in each flow_segment
#define FLOW_SEGMENT_LENGTH 5

// Adjust brightness of LEDs
#define LED_BRIGHTNESS 40 

// Total number of LEDS
#define LED_COUNT (FLOW_SEGMENT_COUNT * FLOW_SEGMENT_LENGTH)

// Array of RFID sensors with grid positions
extern const SensorInfo sensor_info[];

// Create RFIDs
extern RFID RFIDs[];

// LED strip colors
extern CRGB off_color;
extern CRGB error_color;
extern CRGB voltage_colors[];
extern CRGB load_colors[];

// Edit module id if you want to edit test module
#define TEST_MODULE_ID 439560267

#endif

