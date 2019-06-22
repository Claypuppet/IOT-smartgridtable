#include "ring-buffer.h"

#define LEN(a) (sizeof a / sizeof a[0])


RingBuffer ring_create()
{
	RingBuffer r;

	r.size = LEN(r.buf);
	r.start = 0;
	r.count = 0;

	return r;
}

void ring_push(RingBuffer *r, BufferItem item)
{
	size_t i = (r->start + r->count) % r->size;

	if (r->count < r->size) {
		r->count++;
	} else {
		r->start++;
	}

	r->buf[i] = item;
}

BufferItem ring_pop(RingBuffer *r)
{
	size_t i = r->start;

	r->count--;
	r->start = (r->start + 1) % r->size;

	return r->buf[i];
}

size_t ring_length(const RingBuffer *r)
{
	return r->count;
}
