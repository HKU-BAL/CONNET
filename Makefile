CXX = g++
CXXFLAGS = -w -O3 -std=c++1y
LIBFLAG = -lz

gen: gen.o
	$(CXX) $(CXXFLAGS) gen.o -o $@ $(LIBFLAG)
