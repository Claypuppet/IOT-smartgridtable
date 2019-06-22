#include <Arduino.h>

#include "grid.h"

//initialize grid with parsed flow segments
Grid grid_from_parsed_grid(const ParsedGrid *parsed_grid)
{
	Grid grid;

	grid.voltage = parsed_grid->voltage;
	grid.voltage_level = parsed_grid->voltage_level;
	for (size_t i = 0; i < FLOW_SEGMENT_COUNT; i++) {
		grid.flow_segments[i] = flow_segment_from_parsed_flow_segment(&parsed_grid->flow_segments[i]);
	}

	return grid;
}

//Converts byte grid with normal grid
Grid grid_from_bytes(const uint8_t *b)
{
	const ParsedGrid *parsed_grid = (const ParsedGrid *) b;

	return grid_from_parsed_grid(parsed_grid);
}

//Prints grid information
void grid_print(const Grid *grid)
{
	Serial.println("Grid ----");

	Serial.print(" Voltage: ");
	Serial.println(voltage_to_string(grid->voltage));
	Serial.print(" Voltage level: ");
	Serial.println(voltage_level_to_string(grid->voltage_level));

	for (size_t i = 0; i < FLOW_SEGMENT_COUNT; i++) {
		Serial.print("  Flow ");
		Serial.print(i);
		Serial.print(": ");

		flow_segment_print(&grid->flow_segments[i]);
	}
}
