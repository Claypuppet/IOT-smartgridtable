#include "rfid.h"

/* ID of the I2C slave */
#define SLAVE_ID 1

/* Shared RFID reset pin */
#define RFID_RST_PIN A0

/* RFID data pins */
#define RFID0_SDA_PIN 5
#define RFID1_SDA_PIN 6
#define RFID2_SDA_PIN 7
#define RFID3_SDA_PIN 8

/* Number of RFIDs on this Arduino */
#define RFID_COUNT 4

/* RFIDs on this Arduino */
extern RFID RFIDs[];
