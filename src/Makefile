PYLIB = /usr/bin
PYINC = /usr/include/python2.7
CC_SWITCHES =   -g -c -fPIC
SHLIB_LD =      /usr/bin/ld -G -z text
SHLIB_SUFFIX =  .so

pysicl.so: pysicl.c
	gcc pysicl.c ${CC_SWITCHES} \
		-I$(PYINC) -L$(PYLIB)
	${SHLIB_LD} pysicl.o \
		-lpython2.7 -lsicl -o pysicl.so
install:
	cp pysicl.so ..
clean:
	rm -f pysicl.so ../pysicl.so core
