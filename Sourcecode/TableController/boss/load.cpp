#include "load.h"

const char *load_string[] = {
	[LOAD_NORMAL] = "Ok",
	[LOAD_HIGH] = "High",
	[LOAD_CRITICAL] = "Stressed",
};

const char *load_to_string(Load load)
{
	return load_string[load];
}
