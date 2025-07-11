#ifndef __ARDUCAM_H
#define __ARDUCAM_H
#include "bcm283x_board_driver.h"
#include <stdio.h>
#include <string.h>

typedef unsigned char uint8_t; 
typedef unsigned char byte;
typedef u_int16_t uint16_t;
typedef u_int32_t uint32_t;

#define PROGMEM
//ArduCAM CS define
#define     CAM_CS1         17


/****************************************************/
/* Sensor related definition 												*/
/****************************************************/
#define BMP 	0
#define JPEG	1
#define RAW	  	2

#define IMX225		0

#define HCG          0
#define LCG          1
#define NORMAL       2
#define INVERTED     3

/* IMX225 resolution definition */
#define IMX225_640x480 		0	//640x480
#define IMX225_1280x960 	3	//1280x960
#define IMX225_BINNING  	4	

/* Register initialization tables for SENSORs */
/* Terminating list entry for reg */
#define SENSOR_REG_TERM_8BIT                0xFF
#define SENSOR_REG_TERM_16BIT               0xFFFF
/* Terminating list entry for val */
#define SENSOR_VAL_TERM_8BIT                0xFF
#define SENSOR_VAL_TERM_16BIT               0xFFFF
//Define maximum frame buffer size
#define MAX_FIFO_SIZE		0x7FFFFF		//8MByte


#define ARDUCHIP_FIFO      		0x04  //FIFO and I2C control
#define FIFO_CLEAR_MASK    		0x01
#define FIFO_START_MASK    		0x02
#define FIFO_RDPTR_RST_MASK     0x10
#define FIFO_WRPTR_RST_MASK     0x20

#define FIFO_SIZE1				0x42  //Camera write FIFO size[7:0] for burst to read
#define FIFO_SIZE2				0x43  //Camera write FIFO size[15:8]
#define FIFO_SIZE3				0x44  //Camera write FIFO size[18:16]

/****************************************************/
/* ArduChip registers definition 					*/
/****************************************************/
#define	  ARDUCHIP_TEST1		0X00		//test register
#define	  CAPTURE_CONTROL		0X01		//capture control register
#define	  FIFO_CONTROL			0X04		//FIFO control Register Bit[0]: write '1'to clear FIFO 
											//write done flag Bit[1]: write '1' to start capture
#define	  TEST_MODE				0X05		//Test Mode Register
#define   GPIO_WRITE            0X06        //Bit[0]: Sensor reset IO value
                                            //Bit[1]: Sensor power down IO value
                                            //Bit[2]: Sensor power enable IO value
#define	  CPLD_AND_I2C_CONTROL	0X07		//Bit[7]: write '1' to reset CPLD, Bit[1]: write 1,reset I2C; Bit[0]:write 1，Initiate a I2C read operation
#define   I2C_DEV_ADDR			0X0A		//I2C device address
#define   I2C_REG_HIGH			0X0B		//I2C register address high bits
#define   I2C_REG_LOW			0X0C		//I2C register address low bits
#define   I2C_WRTE_CONTROL		0X0D		//I2C register write data,I2C start a write operation
#define   UP_CAT				0X0E
#define   DOWN_CAT				0X0F
#define   JOINT_WAY				0X10
#define   BURST_FIFO_READ		0x3C  		//Burst FIFO read operation
#define   SINGLE_FIFO_READ		0x3D  		//Single FIFO read operation
#define   ARDUCHIP_REV       	0x40 		//ArduCHIP revision

#define   ARDUCHIP_TRIG      	0x41  		//Trigger source
#define   VSYNC_MASK         	0x01
#define   SHUTTER_MASK      	0x02
#define   CAP_DONE_MASK      	0x08

#define   ARDUCHIP_YEAR			0X46		//ArduChip version year
#define   ARDUCHIP_MONTH		0X47		//ArduChip version month
#define   ARDUCHIP_DATE			0X48		//ArduChip version date
#define   DATA_I2C_READ			0X4A
#define   COLUMN_LOW_RESO		0x4B		//Column resolution low 8 bits
#define   COLUMN_HIGH_RESO		0x4C		//Bit[2:0] Column resolution high 3 bits
#define   ROW_LOW_RESO			0x4D
#define   ROW_HIGH_RESO			0x4E
#define   TRACE_ID_8			0x4F
#define   TRACE_ID_7			0x50
#define   TRACE_ID_6			0x51
#define   TRACE_ID_5			0x52
#define   TRACE_ID_4			0x53
#define   TRACE_ID_3			0x54
#define   TRACE_ID_2			0x55
#define   TRACE_ID_1			0x56


/****************************************************************/
/* define a structure for sensor register initialization values */
/****************************************************************/
struct sensor_reg {
	uint16_t reg;
	uint16_t val;
};
/****************************************************************/
/* define a structure for sensor register initialization values */
/****************************************************************/
class ArduCAM 
{
	public:
	ArduCAM( void );
	ArduCAM(byte model ,int CS);
    void ArduCAM_Camera_ON(void);
    void ArduCAM_Camera_OFF(void);
	void InitCAM( void );
	
	void CS_HIGH(void);
	void CS_LOW(void);
	
	void flush_fifo(void);
	void start_capture(void);
	void clear_fifo_flag(void);
	uint8_t read_fifo(void);
	
	uint8_t read_reg(uint8_t addr);
	void write_reg(uint8_t addr, uint8_t data);	
	
	uint32_t read_fifo_length(void);
	void set_fifo_burst(void);
	
	void set_bit(uint8_t addr, uint8_t bit);
	void clear_bit(uint8_t addr, uint8_t bit);
	uint8_t get_bit(uint8_t addr, uint8_t bit);
	void set_mode(uint8_t mode);
 
	uint8_t bus_write(int address, int value);
	uint8_t bus_read(int address);	
 
    void Arducam_bus_detect(void);
    void Arducam_CS_Init(void);
    void resetFirmware();
    unsigned char SPI_transfer(unsigned char temp);

	// Write 8 bit values to 8 bit register address
	int wrSensorRegs8_8(const struct sensor_reg reglist[]);
	
	// Write 16 bit values to 8 bit register address
	int wrSensorRegs8_16(const struct sensor_reg reglist[]);
	
	// Write 8 bit values to 16 bit register address
	int wrSensorRegs16_8(const struct sensor_reg reglist[]);
	
  // Write 16 bit values to 16 bit register address
	int wrSensorRegs16_16(const struct sensor_reg reglist[]);
	
	// Read/write 8 bit value to/from 8 bit register address	
	byte wrSensorReg8_8(int regID, int regDat);
	byte rdSensorReg8_8(uint8_t regID, uint8_t* regDat);
	
	// Read/write 16 bit value to/from 8 bit register address
	byte wrSensorReg8_16(int regID, int regDat);
	byte rdSensorReg8_16(uint8_t regID, uint16_t* regDat);
	
	// Read/write 8 bit value to/from 16 bit register address
	byte wrSensorReg16_8(int regID, int regDat);
	unsigned char rdSensorReg16_8(unsigned int regID, unsigned char* regDat);
	
	// Read/write 16 bit value to/from 16 bit register address
	byte wrSensorReg16_16(int regID, int regDat);
	byte rdSensorReg16_16(uint16_t regID, uint16_t* regDat);
	
    int rdSensorRegs16_8(const struct sensor_reg reglist[]);

	void set_format(byte fmt);
    
    // set IMX225 resolution
	void IMX225_set_RAW_size(uint8_t size);
    
    // Read resolution column
	uint16_t read_resolution_column(void);
	
    // Read resolution row
	uint16_t read_resolution_row(void);
	
    // Return a pointer to trace id
	uint8_t *read_trace_id(void);
    
    // Power down the image sensor with the CPLD,//problem
    void sensor_power_down(void);

    // Power enable the image sensor with the CPLD, //problem
    void sensor_power_enable(void);

    //Image sensor get into a standby mode by setting IMX225 specified registers
    void IMX225_sensor_standby(void);

    // Power on the image sensor by setting IMX225 specified registers
    void IMX225_sensor_on(void);
    
    // Set imx225 gain conversion mode
    void IMX225_gain_conversion_mode(uint8_t mode);
    
    // IMX225 gain set,0.0 dB to 72.0 dB / 0.1 dB step
    void IMX225_set_gain(float val);
    
    // Normal exposure operation,range of val: 0x2 - 0x3df, 0x02 - 0x1f2(binning)
    void IMX225_normal_exposure(uint16_t val);
    
    // Long exposure operation ,range of val : 0x044c - 0x3333, 0x02ff - 0x3333(binning)
    void IMX225_long_exposure(uint16_t val);
    
    // Vertical direction readout inversion control
    void IMX225_vertical_inversion_control(uint8_t mode);
    
    // Horizontal direction readout inversion control
    void IMX225_horizontal_inversion_control(uint8_t mode);
    
    void IMX225_exposure(uint16_t val);
    
	#if defined (RASPBERRY_PI)
    uint8_t transfer(uint8_t data);
	void transfers(uint8_t *buf, uint32_t size);
    #endif

	void transferBytes_(uint8_t * out, uint8_t * in, uint8_t size);
	void transferBytes(uint8_t * out, uint8_t * in, uint32_t size);
	inline void setDataBits(uint16_t bits);
	
  protected:
	volatile uint32_t *P_CS;
	uint32_t B_CS;
	byte m_fmt;
	byte sensor_model;
	byte sensor_addr;
};

#endif
