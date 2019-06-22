#include <Arduino.h>

#include "synced-millis.h"


int32_t diff_millis = 0;

void set_millis(uint32_t received_millis)
{
	diff_millis = received_millis - (int32_t)millis();
}

uint32_t synced_millis()
{
	return millis() + diff_millis;
}


