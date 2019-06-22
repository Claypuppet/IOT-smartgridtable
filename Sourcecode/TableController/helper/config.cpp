#include "config.h"

/* RFIDs on this Arduino */
RFID RFIDs[RFID_COUNT] = {
	RFID_create(RFID0_SDA_PIN, RFID_RST_PIN),
	RFID_create(RFID1_SDA_PIN, RFID_RST_PIN),
	RFID_create(RFID2_SDA_PIN, RFID_RST_PIN),
	RFID_create(RFID3_SDA_PIN, RFID_RST_PIN),
};
