#ifndef LEDSTRIP_H
#define LEDSTRIP_H

#include "flow-segment-state.h"
#include "load.h"
#include "grid.h"

extern bool testReady;

struct LedstripSegment {
	FlowSegmentState state;
	Load load;
	bool direction;
	uint8_t speed;  
	uint8_t position;
};

// Sets up the led strip
void ledstrip_setup();

// Updates the led strip animation
// @param force Set this to true to force an update. Defaults to false
void ledstrip_update(bool force = false);

// Calculates animation position of led strip segment
// @param segment Pointer to the LED strip segment
uint8_t ledstrip_calculate_position(LedstripSegment *segment);

// Shows active or passive flow_segment on led strip segment
// @param segment The segment to show the new flow segment on
// @param first_led The first position to start the flow
void ledstrip_show_flow_segment(LedstripSegment *segment, uint8_t first_led);

// Shows error indication on led strip segment
void ledstrip_show_error(LedstripSegment *segment, uint8_t first_led);

// Sets grid to visualize with led strip
void ledstrip_set_grid(const Grid *grid);

// Sets the LED strip colors
void ledstrip_set_color(uint8_t id, uint32_t rgb);

// Tests ledstrip by color, segments and individual leds
bool ledstrip_test(bool testReady);

// Returns true is the leds of errors should be on
bool ledstrip_errors_showing(uint16_t timing);


#endif
