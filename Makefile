CXX = g++
CXXFLAGS = -fPIC -w -g -O3 -std=c++1y -ansi -pedantic
#LIBFLAG = -lz

all: myextension

libmyextension: myextension.cpp
	$(CXX) $(CXXFLAGS) -o $@ $(LIBFLAG)


clean:
	rm libmyextension
