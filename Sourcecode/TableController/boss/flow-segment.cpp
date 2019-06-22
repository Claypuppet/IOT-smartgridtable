#include <Arduino.h>

#include "flow-segment.h"

//sets flow segment properties with parsed flow segment properties that are received in FLOW_CONFIG_CHANGE_MSG from maincontroller
FlowSegment flow_segment_from_parsed_flow_segment(const ParsedFlowSegment *parsed_flow_segment)
{
	FlowSegment flow_segment;

	flow_segment.state = parsed_flow_segment->state;
	flow_segment.load = parsed_flow_segment->load;
	flow_segment.speed = parsed_flow_segment->speed;
	flow_segment.direction = parsed_flow_segment->direction;

	return flow_segment;
}

//print the state, load, direction(direction or normal), 
void flow_segment_print(const FlowSegment *flow_segment)
{
	Serial.print("State: ");
	Serial.print(flow_segment_state_to_string(flow_segment->state));
	Serial.print(", ");

	Serial.print("Load: ");
	Serial.print(load_to_string(flow_segment->load));
	Serial.print(", ");

	Serial.print("Reversed: ");
	Serial.print(flow_segment->direction ? "yes" : "no");
	Serial.print(", ");

	Serial.print("Speed: ");
	Serial.print(flow_segment->speed);
	Serial.println();
}
