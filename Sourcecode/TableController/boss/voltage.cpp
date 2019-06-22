#include "voltage.h"

const char *voltage_string[] = {
	[VOLTAGE_LOW] = "Low",
	[VOLTAGE_MEDIUM] = "Medium",
	[VOLTAGE_HIGH] = "High",
};

const char *voltage_to_string(Voltage voltage)
{
	return voltage_string[voltage];
}

const char *voltage_level_string[] = {
	[VOLTAGE_LEVEL_NORMAL] = "Normal",
	[VOLTAGE_LEVEL_HIGH] = "High",
	[VOLTAGE_LEVEL_CRITICAL] = "Critical",
	[VOLTAGE_LEVEL_UNSTABLE] = "Unstable",
};

const char *voltage_level_to_string(VoltageLevel voltageLevel)
{
	return voltage_level_string[voltageLevel];
}
