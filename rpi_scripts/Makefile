CXX = g++
CC = gcc

CPP_SRC = ./src/simple_capturing.cpp ./src/ArduCAM.cpp
C_SRC = ./src/bcm283x_board_driver.c ./src/sccb_bus.c

OUT = simple_capturing
CFLAGS = -lpthread

all:
	$(CXX) $(CPP_SRC) $(C_SRC) -o $(OUT) $(CFLAGS)
