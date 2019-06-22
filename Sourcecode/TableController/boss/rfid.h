#ifndef RFID_H
#define RFID_H

#include <MFRC522.h>

// Default authentication key 
extern MFRC522::MIFARE_Key default_key;
 
struct RFID {
	MFRC522 mfrc522;
	bool tag_present;
};

struct RFID_message {
	uint8_t sensor_id;
	bool tag_present;
	uint32_t tag_id;
};

//Creates RFID object
RFID RFID_create(uint8_t ss_pin, uint8_t rst_pin);

//Initializes RFID module
void RFID_init(RFID *RFID);

//Checks if RFID state has changed (tag placed or removed)
bool RFID_state_changed(RFID *RFID);

//Starts authenticated session with RFID tag. This must be called before any read operation on the tag
bool RFID_start_auth(RFID *RFID);

//Stops authenticated session with RFID tag. This must be called to end an authenticated session, otherwise no RFID tags can be detected
void RFID_stop_auth(RFID *RFID);

//Reads RFID tag ID (UID)
bool RFID_tag_read_id(RFID *RFID, RFID_message *msg);

// Prints RFID message
void RFID_message_print(const RFID_message *msg);

#endif
