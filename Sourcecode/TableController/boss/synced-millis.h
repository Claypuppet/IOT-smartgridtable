#ifndef SYNCED_MILLIS_H
#define SYNCED_MILLIS_H

//set millis that is received from maincontroller
void set_millis(uint32_t received_millis);

//synchronizes received time from maincontroller with time on table section
uint32_t synced_millis();

#endif 
