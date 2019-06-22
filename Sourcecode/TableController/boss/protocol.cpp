#include <core/MySensorsCore.h>

#include "protocol.h"

void change_module(uint8_t location, uint32_t module_id)
{
	MyMessage msg(location, MODULE_CHANGE_MSG);

	msg.setDestination(0);
	msg.set(module_id);
	send(msg);
}

void change_neighbor(uint8_t side, uint32_t table_section_id)
{
	MyMessage msg(side, NEIGHBOR_CHANGE_MSG);

	msg.setDestination(0);
	msg.set(table_section_id);
	send(msg);
}

