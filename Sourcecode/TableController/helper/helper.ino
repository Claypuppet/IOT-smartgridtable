#include <SPI.h>
#include <Wire.h>

#include "config.h"

void setup()
{
	/* start SPI for RFID readers */
	SPI.begin();

	/* start I2C as master */
	Wire.begin();

	/* initialize RFID readers */
	for (size_t i = 0; i < RFID_COUNT; i++) {
		RFID_init(&RFIDs[i]);
	}

	Serial.begin(115200);
	Serial.println("setup() finished");
}

void loop()
{
	for (size_t i = 0; i < RFID_COUNT; i++) {
		handle_RFID(&RFIDs[i], i);
	}
}

void handle_RFID(RFID *RFID, uint8_t sensor_id)
{
	/* skip RFID if state has not changed */
	if (!RFID_state_changed(RFID)) {
		return;
	}

	/* create RFID message */
	RFID_message msg = {
		.sensor_id = sensor_id,
		.tag_present = RFID->tag_present,
	};

	/* read tag ID if tag is present */
	if (msg.tag_present) {
		bool tag_id_read = RFID_start_auth(RFID) &&
		                   RFID_tag_read_id(RFID, &msg);

		RFID_stop_auth(RFID);

		/* ignore RFID if tag ID could not be read */
		if (!tag_id_read) {
			return;
		}
	}

	handle_RFID_message(&msg);
}

void handle_RFID_message(const RFID_message *msg)
{
	/* print RFID message */
	RFID_message_print(msg);

	/* send RFID message to I2C slave */
	Wire.beginTransmission(SLAVE_ID);
	Wire.write((const char *)msg, sizeof *msg);

	Wire.endTransmission();
}
