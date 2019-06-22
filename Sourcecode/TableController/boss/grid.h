#ifndef GRID_H
#define GRID_H

#include "config.h"
#include "flow-segment.h"
#include "voltage.h"

//Grid properties
struct Grid {
	Voltage voltage;
	VoltageLevel voltage_level;
	FlowSegment flow_segments[FLOW_SEGMENT_COUNT];
};

//Parsed grid properties
struct ParsedGrid {
	uint8_t : 4; 				// 4 bits unused bits in header byte
	uint8_t voltage_level : 2; 	// 2 bits for voltage level in header byte
	uint8_t voltage: 2; 		// 2 bits for voltage in header byte
	ParsedFlowSegment flow_segments[FLOW_SEGMENT_COUNT]; //rest of bytes for flow segments
};

//Converts parsed grid to normal grid
Grid grid_from_parsed_grid(const ParsedGrid *parsed_grid);

//Converts byte grid to normal grid
Grid grid_from_bytes(const uint8_t *b);

//Prints grid information
void grid_print(const Grid *grid);

#endif
