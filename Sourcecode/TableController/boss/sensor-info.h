#ifndef SENSOR_INFO_H
#define SENSOR_INFO_H

//Sensor types, module sensors for rfids on top of the table, table section sensors for rfids on sides of the table (see config.cpp file for layout)
enum SensorType {
	MODULE_SENSOR,
	TABLE_SECTION_SENSOR,
};

//properties of table sensors
struct SensorInfo {
	SensorType type;
	uint8_t location;
};

#endif
