CC = $(CROSS_COMPILE)gcc
AR = $(CROSS_COMPILE)ar

LIBRARY = libbunga.a
PREFIX ?= /usr/local
INC += include
INC += $(BUNGA_INC)
CFLAGS = -Wall -O2 $(INC:%=-I%) -c
CFLAGS += $(CFLAGS_EXTRA)

.PHONY: library install clean

library: $(LIBRARY)

install:
	find include -type f -exec install -Dm 644 "{}" "$(PREFIX)/{}" \;
	mkdir -p $(PREFIX)/lib
	install -m 644 $(LIBRARY) $(PREFIX)/lib

clean:
	rm $(LIBRARY)

$(LIBRARY):
	$(CC) $(CFLAGS) src/bunga.c -o bunga.o
	$(CC) $(CFLAGS) src/bunga_server.c -o bunga_server.o
	$(AR) cr $(LIBRARY) bunga.o bunga_server.o
