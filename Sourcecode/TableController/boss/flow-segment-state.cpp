#include "flow-segment-state.h"

//flow_segment state initialization 
const char *flow_segment_state_string[] = {
	[FLOW_SEGMENT_STATE_OFF] = "Off",
	[FLOW_SEGMENT_STATE_ERROR] = "Error",
	[FLOW_SEGMENT_STATE_PASSIVE] = "Passive",
	[FLOW_SEGMENT_STATE_ACTIVE] = "Active",
};


// Converts flow_segment state to string
const char *flow_segment_state_to_string(FlowSegmentState flow_segment_state)
{
	return flow_segment_state_string[flow_segment_state];
}
