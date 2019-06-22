#ifndef FLOW_SEGMENT_STATE_H
#define FLOW_SEGMENT_STATE_H

enum FlowSegmentState {
	FLOW_SEGMENT_STATE_OFF,  //leds off
	FLOW_SEGMENT_STATE_ERROR, //leds red blinking
	FLOW_SEGMENT_STATE_PASSIVE, //leds only background color
	FLOW_SEGMENT_STATE_ACTIVE,  //leds background and foreground color
};


// Converts flow_segment state to string
const char *flow_segment_state_to_string(FlowSegmentState flow_segment_state);

#endif
