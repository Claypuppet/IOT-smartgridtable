#ifndef FLOW_SEGMENT_H
#define FLOW_SEGMENT_H

#include "flow-segment-state.h"
#include "load.h"

//Flow segment properties 
struct FlowSegment {
	FlowSegmentState state;
	Load load;
	bool direction; //true == producing (flowing from module) and false == consuming (flowing to module)
	uint8_t speed;
};

//Parsed flow segment properties
struct ParsedFlowSegment {
	uint8_t state: 2;
	uint8_t load: 2;
	uint8_t direction: 1;
	uint8_t speed: 3;
};

//Converts parsed flow_segment to normal flow_segment
FlowSegment flow_segment_from_parsed_flow_segment(const ParsedFlowSegment *parsed_flow_segment);


//Prints flow_segment information
void flow_segment_print(const FlowSegment *flow_segment);

#endif
