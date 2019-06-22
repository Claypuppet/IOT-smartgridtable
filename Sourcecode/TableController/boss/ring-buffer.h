#ifndef RING_BUFFER_H
#define RING_BUFFER_H

#include "rfid.h"

//BufferItem of type RFID message, as it is received by I2C communication
typedef RFID_message BufferItem;

//Ring buffer to put received RFID messages, received by I2C communication
struct RingBuffer {
	BufferItem buf[8];
	size_t size;
	size_t start;
	size_t count;
};

//Call this to create ringbuffer 
RingBuffer ring_create();

//Pushes new item on ringbuffer
void ring_push(RingBuffer *r, BufferItem item);

//Pops last item off ringbuffer
BufferItem ring_pop(RingBuffer *r);

//Determine length of ringbuffer
size_t ring_length(const RingBuffer *r);

#endif
