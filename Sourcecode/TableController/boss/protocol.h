#ifndef PROTOCOL_H
#define PROTOCOL_H

#include <core/MyMessage.h>

//Message types as described in mysensors library: https://www.mysensors.org/download/serial_api_20
enum MessageType {
	// outgoing messages 
	REBOOT_BOSS_AND_HELPER_MSG = V_VAR1,
	MODULE_CHANGE_MSG = V_VAR2,
	NEIGHBOR_CHANGE_MSG = V_VAR3,

	// incoming messages 
	FLOW_CONFIG_CHANGE_MSG = V_VAR4,
	TIME_SYNC_MSG = V_VAR5,
	COLOR_CHANGE_MSG = V_RGB,
};

//Sends change module (placed or removed) message to main-controller
void change_module(uint8_t location, uint32_t module_id);

//Sends neighbor connected/removed message to main-controller
void change_neighbor(uint8_t side, uint32_t table_section_id);

#endif
