#ifndef LOAD_H
#define LOAD_H

// Load properties 
enum Load {
	LOAD_NORMAL, //leds by default green
	LOAD_HIGH,   //leds by default orange
	LOAD_CRITICAL, //leds by default red
};

//Converts load to string
const char *load_to_string(Load load);

#endif
