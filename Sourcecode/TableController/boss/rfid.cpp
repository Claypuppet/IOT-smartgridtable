#include <Arduino.h>

#include "rfid.h"

// Prepare key - all keys are set to FFFFFFFFFFFF at chip delivery from the factory.
  MFRC522::MIFARE_Key default_key = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF};

RFID RFID_create(uint8_t ss_pin, uint8_t rst_pin)
{
	RFID RFID;

	pinMode(rst_pin, OUTPUT);
	digitalWrite(rst_pin, LOW);
	pinMode(ss_pin, OUTPUT);
	digitalWrite(ss_pin, HIGH);

	RFID.mfrc522 = MFRC522(ss_pin, rst_pin);
	RFID.tag_present = false;

	return RFID;
}

void RFID_init(RFID *RFID)
{
	RFID->mfrc522.PCD_Init();
}

bool RFID_state_changed(RFID *RFID)
{
	uint8_t buf[2];
	uint8_t buf_size = sizeof buf;

	bool was_tag_present = RFID->tag_present;

	RFID->tag_present =
	    RFID->mfrc522.PICC_RequestA(buf, &buf_size) == MFRC522::STATUS_OK ||
	    RFID->mfrc522.PICC_WakeupA(buf, &buf_size) == MFRC522::STATUS_OK;

	if (RFID->tag_present && !was_tag_present) {
		RFID->mfrc522.PICC_HaltA();
	}

	return was_tag_present != RFID->tag_present;
}

bool RFID_start_auth(RFID *RFID)
{
	uint8_t buf[2]; 
	uint8_t buf_size = sizeof buf;
	uint8_t block_addr = 4;
  uint8_t auth_cmd = MFRC522::PICC_CMD_MF_AUTH_KEY_A;
  
	RFID->mfrc522.PICC_WakeupA(buf, &buf_size);
	RFID->mfrc522.PICC_ReadCardSerial();

	return RFID->mfrc522.PCD_Authenticate(auth_cmd, block_addr, &default_key, &RFID->mfrc522.uid) == MFRC522::STATUS_OK;
}

void RFID_stop_auth(RFID *RFID)
{
	RFID->mfrc522.PICC_HaltA();
	RFID->mfrc522.PCD_StopCrypto1();
}

bool RFID_tag_read_id(RFID *RFID, RFID_message *msg)
{
  msg->tag_id = RFID->mfrc522.uid.uidByte[0] | ((uint32_t)RFID->mfrc522.uid.uidByte[1] << 8) | ((uint32_t)RFID->mfrc522.uid.uidByte[2] << 16) | ((uint32_t)RFID->mfrc522.uid.uidByte[3] << 24);
  return true;
}

void RFID_message_print(const RFID_message *msg)
{
	Serial.println("RFID Event ----");

	Serial.print("  Sensor ID: ");
	Serial.println(msg->sensor_id);

	Serial.print("  Tag state: ");
	Serial.println(msg->tag_present ? "Present" : "Removed");

	if (msg->tag_present) {
		Serial.print("  Tag ID: ");
		Serial.println(msg->tag_id, DEC);
	}
}
