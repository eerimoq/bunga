test:
	coverage run --source=bunga setup.py test
	$(MAKE) -C lib

coverage:
	coverage html
	echo "Open htmlcov/index.html in firefox."

generate:
	cd bunga && \
	    messi generate_py_source -s client -I ../proto ../proto/bunga.proto
	messi generate_c_source -s server proto/bunga.proto
	mv bunga.h bunga_server.h lib/include
	mv bunga.c bunga_server.c lib/src
