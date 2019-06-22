/**
   SMART GRID TABLE TESTS
*/

#define LED_COUNT 100 // 100 leds on one table part
#define SECTION_SIZE 5 // LED section size
#define LEDSTRIP_DATA_PIN 3
#define LEDSTRIP_CLK_PIN 2
#define DEFAULT_BRIGHTNESS 20

// LED library used for the APA102 LED strips
#include <FastLED.h>

CRGB leds[LED_COUNT];
char received_data;
boolean new_data = false;
uint32_t previous_time = 0;
int i = 0;

void setup()
{
  Serial.begin(115200);

  // Initialize LED strip
  FastLED.addLeds<SK9822, LEDSTRIP_DATA_PIN, LEDSTRIP_CLK_PIN, BGR>(leds, LED_COUNT);
  FastLED.setBrightness(DEFAULT_BRIGHTNESS);
  for (i = 0; i < LED_COUNT; i++)
  {
    leds[i] = CRGB::Black;
  }
  FastLED.show();

  Serial.println("Smart grid table - BOSS TESTING PROGRAM");
  Serial.println("");
  Serial.println("Available tests:");
  Serial.println("r - set all leds to red");
  Serial.println("g - set all leds to green");
  Serial.println("b - set all leds to blue");
  Serial.println("w - set all leds to white");
  Serial.println("o - turn all the leds off");
  Serial.println("s - turn sections 1-20 on, one by one");
  Serial.println("l - turn leds on and off, one by one");
  Serial.println("v - test brightness from 0 to 255, in steps of 5");
}

void loop()
{
  if (new_data == true)
  {
    if (received_data == 'w')
    {
      for (uint8_t j = 0; j < LED_COUNT; j++)
      {
        leds[j] = CRGB::White;
      }
      new_data = false;
    } 
    else if (received_data == 'r')
    {
      for (uint8_t j = 0; j < LED_COUNT; j++)
      {
        leds[j] = CRGB::Red;
      }
      new_data = false;
    } 
    else if (received_data == 'b')
    {
      for (uint8_t j = 0; j < LED_COUNT; j++)
      {
        leds[j] = CRGB::Blue;
      }
      new_data = false;
    } 
    else if (received_data == 'g')
    {
      for (uint8_t j = 0; j < LED_COUNT; j++)
      {
        leds[j] = CRGB::Green;
      }
      new_data = false;
    } 
    else if (received_data == 'o')
    {
      for (uint8_t j = 0; j < LED_COUNT; j++)
      {
        leds[j] = CRGB::Black;
      }
      new_data = false;
    } 
    else if (received_data == 's')
    {
      if (i < LED_COUNT)
      {
        for (uint8_t j = 0; j < SECTION_SIZE; ++j)
        {
          leds[i + j] = CRGB::White;
        }
        if (is_time_elapsed(200))
        {
          for (uint8_t j = 0; j < SECTION_SIZE; ++j)
          {
            leds[i + j] = CRGB::Black;
          }
          i += SECTION_SIZE;
        }
      }
      if (i >= LED_COUNT)
      {
        i = 0;
        new_data = false;
      }
    } 
    else if (received_data == 'l')
    {
      if (i < LED_COUNT)
      {
        leds[i] = CRGB::White;
      }
      if (is_time_elapsed(80))
      {
        ++i;
      }
      if (i >= LED_COUNT)
      {
        i = 0;
        for (uint8_t j = 0; j < LED_COUNT; ++j)
        {
          leds[j] = CRGB::Black;
        }
        new_data = false;
      }
    } 
//    else if (received_data == 'v')
//    {
//      FastLED.setBrightness(0);
//      for (uint8_t i = 0; i < LED_COUNT; ++i)
//      {
//        leds[i] = CRGB::White;
//        FastLED.show();
//      }
//      for (uint16_t i = 5; i < 256; i += 5)
//      {
//        FastLED.setBrightness(i);
//        FastLED.show();
//        delay(50);
//      }
//      for (uint8_t i = 0; i < LED_COUNT; ++i)
//      {
//        leds[i] = CRGB::Black;
//      }
//      FastLED.setBrightness(DEFAULT_BRIGHTNESS);
//    }
    FastLED.show();
  }
}

void serialEvent()
{
  received_data = Serial.read();
  i = 0;
  for (int j = 0; j < LED_COUNT; j++)
  {
    leds[j] = CRGB::Black;
  }
  FastLED.show();
  new_data = true;
}

boolean is_time_elapsed(uint32_t delay_time) {
  uint32_t current_time = millis();

  if (current_time - previous_time > delay_time) {
    previous_time = current_time;
    return true;
  }
  return false;
}

