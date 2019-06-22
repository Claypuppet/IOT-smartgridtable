#ifndef CONFIG_H
#define CONFIG_H

#include <FastLED.h>

// Enable the MY_DEBUG define to show debug messages
//#define MY_DEBUG

// Table part ID
#define TABLE_PART_ID 7 /* TABLE PART ID 7 IS FOR EMULATING PURPOSES ONLY */

// MySensors radio defines
#define MY_RADIO_NRF24
#define MY_RF24_PA_LEVEL RF24_PA_HIGH
#define MY_RF24_CHANNEL 93
#define MY_NODE_ID TABLE_PART_ID

#endif

