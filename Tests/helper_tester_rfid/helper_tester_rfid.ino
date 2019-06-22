/*
Testsketch to test 8 RFID readers on one Arduino Nano for the Smart Grid Table (prototype 2 & 3)
Made by: Joris van Zeeland
 */

#include <SPI.h>
#include <MFRC522.h>
#include <Wire.h> 

#define RST_PIN         A0          // digital or analog pins doesn't matter
#define SS_1_PIN        8         
#define SS_2_PIN        7           
#define SS_3_PIN        6          
#define SS_4_PIN        5                

#define NR_OF_READERS   4

byte ssPins[] = {SS_1_PIN, SS_2_PIN, SS_3_PIN, SS_4_PIN};

MFRC522 mfrc522[NR_OF_READERS];   // Create MFRC522 instance.

byte x = 0;

void setup() {

  Serial.begin(115200);
  while (!Serial);    // Do nothing if no serial port is opened 

  SPI.begin();        // Init SPI bus
  Wire.begin();
  
  delay(200);
  for (uint8_t reader = 0; reader < NR_OF_READERS; reader++) {
    mfrc522[reader].PCD_Init(ssPins[reader], RST_PIN); // Init each MFRC522 reader
    delay(100);
    Serial.print(F("Reader "));
    Serial.print(reader);
    Serial.print(F(": "));
    mfrc522[reader].PCD_DumpVersionToSerial();
  }
}

void loop() {

  for (uint8_t reader = 0; reader < NR_OF_READERS; reader++) {
    // Look for new cards

    if (mfrc522[reader].PICC_IsNewCardPresent() && mfrc522[reader].PICC_ReadCardSerial()) {
      Serial.print(F("Reader "));
      Serial.print(reader);
      // Show some details the tag/card
      Serial.print(F(": Card UID:"));
      dump_byte_array(mfrc522[reader].uid.uidByte, mfrc522[reader].uid.size);
      Serial.println();
      Serial.print(F("PICC type: "));
      MFRC522::PICC_Type piccType = mfrc522[reader].PICC_GetType(mfrc522[reader].uid.sak);
      Serial.println(mfrc522[reader].PICC_GetTypeName(piccType));
      Serial.println(mfrc522[reader].uid.size, HEX);
    } 
  } 
}

/**
 * Dump a byte array as hex values to Serial.
 */
void dump_byte_array(byte *buffer, byte bufferSize) {
  for (byte i = 0; i < bufferSize; i++) {
    Serial.print(buffer[i] < 0x10 ? " 0" : " ");
    Serial.print(buffer[i], HEX);
    
    Wire.beginTransmission(8);
    Wire.write(buffer[i]);
    Wire.endTransmission();
  }
}
