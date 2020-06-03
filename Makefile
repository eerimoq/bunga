test:
	python3 setup.py test
	python3 tests/test_command_line.py
	$(MAKE) -C lib

generate:
	cd bunga && \
	    messi generate_py_source -s client -I ../proto ../proto/bunga.proto
	messi generate_c_source -s server proto/bunga.proto
	mv bunga.h bunga_server.h lib/include
	mv bunga.c bunga_server.c lib/src
