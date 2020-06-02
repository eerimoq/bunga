test:
	python3 setup.py test
	$(MAKE) -C lib

generate:
	cd bunga && \
	    messi generate_py_source -s client -I ../proto ../proto/bunga.proto
