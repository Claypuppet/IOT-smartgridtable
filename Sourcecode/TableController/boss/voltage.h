#ifndef VOLTAGE_H
#define VOLTAGE_H

//Voltage categories
enum Voltage {
	VOLTAGE_LOW,
	VOLTAGE_MEDIUM,
	VOLTAGE_HIGH,
};

//Voltage level categories
enum VoltageLevel {
	VOLTAGE_LEVEL_NORMAL,
	VOLTAGE_LEVEL_HIGH,
	VOLTAGE_LEVEL_CRITICAL,
	VOLTAGE_LEVEL_UNSTABLE,
};

// Converts voltage (level) to string
const char *voltage_to_string(Voltage voltage);
const char *voltage_level_to_string(VoltageLevel voltageLevel);

#endif
