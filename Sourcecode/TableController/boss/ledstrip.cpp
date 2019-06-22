#include <FastLED.h>

#include "config.h"
#include "ledstrip.h"
#include "synced-millis.h"

LedstripSegment segments[FLOW_SEGMENT_COUNT];
CRGB leds[LED_COUNT];
Voltage voltage;
VoltageLevel voltageLevel;
bool testReady = true;

//initialize FastLed library and ledstrip 
void ledstrip_setup()
{  
#ifndef LEDSTRIP_TYPE_WITHOUT_CLOCK  
  FastLED.addLeds<LEDSTRIP_TYPE, LEDSTRIP_DATA_PIN, LEDSTRIP_CLK_PIN, BGR>(leds, LED_COUNT);
#else
  FastLED.addLeds<LEDSTRIP_TYPE_WITHOUT_CLOCK, LEDSTRIP_DATA_PIN, GRB>(leds, LED_COUNT);
#endif

  //initialize leds on error(red) color, so that if maincontroller hasn't send flow config message yet, you'll see red led's
  for (uint8_t i = 0; i < LED_COUNT; i++) {
    leds[i] = error_color;
  }

  FastLED.setBrightness(LED_BRIGHTNESS);
  FastLED.show();
}

//update ledstrips according to received flow message
void ledstrip_update(bool force)
{
  bool update = false;

  for (uint8_t i = 0; i < FLOW_SEGMENT_COUNT; i++) {
    uint8_t first_led = i * FLOW_SEGMENT_LENGTH;
    uint8_t position = ledstrip_calculate_position(&segments[i]);

    if (!force && position == segments[i].position && voltageLevel != VOLTAGE_LEVEL_UNSTABLE) {
      continue;
    }

    segments[i].position = position;

    if (segments[i].state == FLOW_SEGMENT_STATE_OFF) {
      for (uint8_t led = 0; led < FLOW_SEGMENT_LENGTH; led++) {
        leds[first_led + led] = off_color;
      }
    } else if (segments[i].state == FLOW_SEGMENT_STATE_ERROR) {
      ledstrip_show_error(&segments[i], first_led);
    } else {
      ledstrip_show_flow_segment(&segments[i], first_led);
    }

    update = true;
  }

  if (update) {
    //update all ledstrips
    FastLED.show();
  }
}

uint8_t ledstrip_calculate_position(LedstripSegment *segment)
{
  uint32_t now = synced_millis();

  if (segment->state == FLOW_SEGMENT_STATE_OFF) {
    return 0;
  } else if (segment->state == FLOW_SEGMENT_STATE_ERROR) {
    return ledstrip_errors_showing(200);
  } else if (segment->state == FLOW_SEGMENT_STATE_PASSIVE) {
    return 0;
  } else if (segment->state == FLOW_SEGMENT_STATE_ACTIVE) {
    uint32_t delay = (150 * (4 - segment->speed)) * ((float) 5 / (float) FLOW_SEGMENT_LENGTH);
    uint8_t position = (now / delay) % FLOW_SEGMENT_LENGTH;

    return segment->direction ? FLOW_SEGMENT_LENGTH - 1 - position : position;
  }
}

bool ledstrip_errors_showing(uint16_t timing){
  // Returns true is the leds of errors should be on
  return (synced_millis() / timing) % 2;
}

void ledstrip_show_flow_segment(LedstripSegment *segment, uint8_t first_led)
{
  // apply voltage color
  for (uint8_t i = 0; i < FLOW_SEGMENT_LENGTH; i++) {
    CRGB color = voltage_colors[voltage];

    // If voltage level is normal, brightness is 2/5 of the defaul
    if(voltageLevel == VOLTAGE_LEVEL_NORMAL){
      color /= 2.5; // 1 / 2.5
    }
    // If voltage level is high, brightness is 2/3 of the default
    else if(voltageLevel == VOLTAGE_LEVEL_HIGH){
      color /= 1.5; // 1 / 1.5
    }
    // If voltage level is critical, default brightness
    else if(voltageLevel == VOLTAGE_LEVEL_CRITICAL){
      // No changes
    }
    // If voltage level is unstable, blink voltage leds
    else if(voltageLevel == VOLTAGE_LEVEL_UNSTABLE){
      color /= ledstrip_errors_showing(300) ? 2.5 : 1; // blink between normal and critical brightness
    }

    leds[first_led + i] = color;
  }

  // apply load color if flow_segment is active
  if (segment->state == FLOW_SEGMENT_STATE_ACTIVE) {
    leds[first_led + segment->position] = load_colors[segment->load];
  }
}

void ledstrip_show_error(LedstripSegment *segment, uint8_t first_led)
{
  CRGB color = segment->position == 0 ? off_color : error_color;

  for (uint8_t i = 0; i < FLOW_SEGMENT_LENGTH; ++i) {
    leds[first_led + i] = color;
  }
}

void ledstrip_set_grid(const Grid *grid)
{
  // Set voltage properties
  voltage = grid->voltage;
  voltageLevel = grid->voltage_level;

  // Set flow segment properties
  for (uint8_t i = 0; i < FLOW_SEGMENT_COUNT; i++) {
    const FlowSegment *flow_segment = &grid->flow_segments[i];

    segments[i].state = flow_segment->state;
    segments[i].load = flow_segment->load;
    segments[i].direction = flow_segment->direction;
    segments[i].speed = flow_segment->speed;
  }
}

void ledstrip_set_color(uint8_t id, uint32_t rgb)
{
  CRGB color = CRGB(rgb);
  switch (id) {
    case 0:
      voltage_colors[VOLTAGE_LOW] = color;
      break;
    case 1:
      voltage_colors[VOLTAGE_MEDIUM] = color;
      break;
    case 2:
      voltage_colors[VOLTAGE_HIGH] = color;
      break;
    case 3:
      load_colors[LOAD_NORMAL] = color;
      break;
    case 4:
      load_colors[LOAD_HIGH] = color;
      break;
    case 5:
      load_colors[LOAD_CRITICAL] = color;
      break;
  }
}

bool ledstrip_test(bool testReady) {
  if (testReady) {
    return false;
  } else {
    //COLOR TEST
    for (uint8_t i = 0; i < LED_COUNT; i++)
    {
      leds[i] = CRGB::Red;
    }
    FastLED.show();
    delay(1000);
    for (uint8_t i = 0; i < LED_COUNT; i++)
    {
      leds[i] = CRGB::Green;
    }
    FastLED.show();
    delay(1000);
    for (uint8_t i = 0; i < LED_COUNT; i++)
    {
      leds[i] = CRGB::Blue;
    }
    FastLED.show();
    delay(1000);
    // FLOW_SEGMENT SEGMENT TEST
    for (uint8_t i = 0; i < LED_COUNT; i += FLOW_SEGMENT_LENGTH)
    {
      for (uint8_t j = 0; j < FLOW_SEGMENT_LENGTH; ++j)
      {
        leds[i + j] = CRGB::White;
      }
      FastLED.show();
      delay(200);
      for (uint8_t j = 0; j < FLOW_SEGMENT_LENGTH; ++j)
      {
        leds[i + j] = CRGB::Black;
      }
      FastLED.show();
    }
    // LED BY LED TEST
    for (uint8_t i = 0; i < LED_COUNT; ++i)
    {
      leds[i] = CRGB::White;
      FastLED.show();
      delay(50);
    }
    for (uint8_t i = 0; i < LED_COUNT; ++i)
    {
      leds[i] = CRGB::Black;
    }
    Serial.println("einde test");
    return true;
  }
}



