#include "ArduCAM.h"
#include "sccb_bus.h"
#include "imx225_regs.h"

unsigned char sensor_model = 0;
unsigned char sensor_addr = 0;
uint8_t trace_id_data[8];

ArduCAM::ArduCAM(){
    sensor_model = IMX225;
    sensor_addr = 0x34;
}

ArduCAM :: ArduCAM(byte mode, int CS){
    if(CS >= 0){
        B_CS = CS;
    }
    sensor_model = mode;
    switch (sensor_model)
        {     
         case IMX225:
            sensor_addr = 0x34;
            break;
        }
}
void  ArduCAM::ArduCAM_Camera_ON(void){
    pinMode(27, OUTPUT);
    digitalWrite(27, HIGH);
    delay_ms(1000);
}
void  ArduCAM::ArduCAM_Camera_OFF(void){
    pinMode(27, OUTPUT);
    digitalWrite(27, LOW);
    delay_ms(1000);
}
void  ArduCAM::Arducam_CS_Init(void){
    pinMode(B_CS, OUTPUT);
    digitalWrite(B_CS, HIGH);
}


void ArduCAM::InitCAM() 
{
  switch (sensor_model)
  {
	case IMX225:
		{
			write_reg(0x05, 0x00);
			write_reg(0x0A, 0x34);
			write_reg(0x0E, 0x0f);// Number of rows cropped above
			write_reg(0x0F, 0x00);
			write_reg(0x10, 0x00);
			//write_reg(0x11, 0x05);
			//write_reg(0x12, 0x20);
			//write_reg(0x13, 0x03);
			//write_reg(0x14, 0xD3);		
			
		  wrSensorReg16_8(0x3000, 0x00);
		  wrSensorReg16_8(0x3002, 0x01);
		  wrSensorReg16_8(0x3005, 0x01);
		  wrSensorReg16_8(0x3006, 0x00);
		  wrSensorReg16_8(0x3007, 0x00);
		  wrSensorReg16_8(0x3009, 0x01);
		  wrSensorReg16_8(0x320c, 0xcf);
		  wrSensorReg16_8(0x300f, 0x00);
		  wrSensorReg16_8(0x310f, 0x0f);
		  wrSensorReg16_8(0x3110, 0x0e);
		  wrSensorReg16_8(0x3111, 0xe7);
		  wrSensorReg16_8(0x3012, 0x2c);
		  wrSensorReg16_8(0x3112, 0x9c);
		  wrSensorReg16_8(0x3013, 0x01);
		  wrSensorReg16_8(0x3113, 0x83);
		  wrSensorReg16_8(0x3014, 0x3c);
		  wrSensorReg16_8(0x3015, 0x00);
		  wrSensorReg16_8(0x3114, 0x10);
		  wrSensorReg16_8(0x3115, 0x42);
		  wrSensorReg16_8(0x3016, 0x09);
          
		  wrSensorReg16_8(0x3018, 0x4C);
		  wrSensorReg16_8(0x3019, 0x04);
		  wrSensorReg16_8(0x301a, 0x00);
		  wrSensorReg16_8(0x301b, 0x94);
          wrSensorReg16_8(0x301c, 0x11);
          
          
		  wrSensorReg16_8(0x301d, 0xc2);
		  wrSensorReg16_8(0x3020, 0x58);
		  wrSensorReg16_8(0x3021, 0x02);
		  wrSensorReg16_8(0x3022, 0x00);
		  wrSensorReg16_8(0x3128, 0x1e);
		  wrSensorReg16_8(0x3049, 0x0a);
		  wrSensorReg16_8(0x324c, 0x40);
		  wrSensorReg16_8(0x324d, 0x03);
		  wrSensorReg16_8(0x305c, 0x2c);
		  wrSensorReg16_8(0x305d, 0x00);
		  wrSensorReg16_8(0x305e, 0x2C);
		  wrSensorReg16_8(0x305f, 0x00);
		  wrSensorReg16_8(0x3261, 0xe0);
		  wrSensorReg16_8(0x3262, 0x02);
		  wrSensorReg16_8(0x326e, 0x2f);
		  wrSensorReg16_8(0x326f, 0x30);
		  wrSensorReg16_8(0x3070, 0x02);
		  wrSensorReg16_8(0x3270, 0x03);
		  wrSensorReg16_8(0x3071, 0x01);
		  wrSensorReg16_8(0x3298, 0x00);
		  wrSensorReg16_8(0x329a, 0x12);
		  wrSensorReg16_8(0x329b, 0xf1);
		  wrSensorReg16_8(0x329c, 0x0c);
		  wrSensorReg16_8(0x309e, 0x22);
		  wrSensorReg16_8(0x30a5, 0xfb);
		  wrSensorReg16_8(0x30a6, 0x02);
		  wrSensorReg16_8(0x30b3, 0xff);
		  wrSensorReg16_8(0x30b4, 0x01);
		  wrSensorReg16_8(0x30b5, 0x42);
		  wrSensorReg16_8(0x30b8, 0x10);
		  wrSensorReg16_8(0x30c2, 0x01);
		  wrSensorReg16_8(0x31ed, 0x38);
		  wrSensorReg16_8(0x3054, 0x67);
		  wrSensorReg16_8(0x3043, 0x00);
		  wrSensorReg16_8(0x3002, 0x00);
		  wrSensorReg16_8(0x3044, 0x01);
		  wrSensorReg16_8(0x3049, 0x0A);
          
          // Gain conversion, initialize to HCG mode
		  //wrSensorReg16_8(0x3009, 0x11);
        
          
          wrSensorReg16_8(0x3357, 0xc0);
          wrSensorReg16_8(0x3358, 0x03);
          
          
		  delay_ms(200);
		}
     default:
     break;
  }
}

void ArduCAM:: CS_HIGH()
{
    delay_us(1);
 	digitalWrite(B_CS, HIGH);					
}

void ArduCAM:: CS_LOW()
{
    delay_us(1);
 	digitalWrite(B_CS, LOW);						    
}

void ArduCAM:: set_format(unsigned char fmt)
{
  if (fmt == BMP)
    m_fmt = BMP;
  else if(fmt == RAW)
  	m_fmt = RAW;
  else
    m_fmt = JPEG;
}

unsigned char ArduCAM:: bus_read(int address)
{
	unsigned char value;
    CS_LOW();
    delay_us(150);
	spiSendReceive(address);
	value = spiSendReceive(0x00);
	CS_HIGH();
	return value;
}
unsigned char ArduCAM:: SPI_transfer(unsigned char temp)
{
  	unsigned char value = spiSendReceive(0x00);
    return value;
}
unsigned char ArduCAM:: bus_write(int address,int value)
{	
	CS_LOW();
    delay_us(150);
	spiSendReceive(address);
	spiSendReceive(value);
	CS_HIGH();
	return 1;
}

unsigned char ArduCAM:: read_reg(unsigned char addr)
{
	unsigned char readData;
	readData = bus_read(addr & 0x7F);
	return readData;
}
void ArduCAM:: write_reg(unsigned char addr, unsigned char data)
{
	 bus_write(addr | 0x80, data); 
}

unsigned char ArduCAM:: read_fifo()
{
	unsigned char data;
	data = bus_read(SINGLE_FIFO_READ);
	return data;
}
void ArduCAM:: set_fifo_burst()
{
    delay_us(150);
	spiSendReceive(BURST_FIFO_READ);
}


void ArduCAM:: flush_fifo()
{
	write_reg(ARDUCHIP_FIFO, FIFO_CLEAR_MASK);
}

void ArduCAM:: start_capture()
{
	write_reg(ARDUCHIP_FIFO, FIFO_START_MASK);
}

void ArduCAM:: clear_fifo_flag( )
{
	write_reg(ARDUCHIP_FIFO, FIFO_CLEAR_MASK);
}

unsigned int ArduCAM:: read_fifo_length()
{
	unsigned int len1,len2,len3,len=0;
	len1 = read_reg(FIFO_SIZE1);
  len2 = read_reg(FIFO_SIZE2);
  len3 = read_reg(FIFO_SIZE3) & 0x7f;
  len = ((len3 << 16) | (len2 << 8) | len1) & 0x07fffff;
	return len;	
}

//Set corresponding bit  
void ArduCAM:: set_bit(unsigned char addr, unsigned char bit)
{
	unsigned char temp;
	temp = read_reg(addr);
	write_reg(addr, temp | bit);
}
//Clear corresponding bit 
void ArduCAM:: clear_bit(unsigned char addr, unsigned char bit)
{
	unsigned char temp;
	temp = read_reg(addr);
	write_reg(addr, temp & (~bit));
}

//Get corresponding bit status
unsigned char ArduCAM:: get_bit(unsigned char addr, unsigned char bit)
{
  unsigned char temp;
  temp = read_reg(addr);
  temp = temp & bit;
  return temp;
}



unsigned char ArduCAM:: wrSensorReg8_8(int regID, int regDat)
{
	delay_us(10);
	sccb_bus_start();                          
	if(sccb_bus_write_byte(sensor_addr) == 0)         
	{
		sccb_bus_stop();                        
		return 1;
	}
	delay_us(10);
	if(sccb_bus_write_byte(regID) == 0)
	{
		sccb_bus_stop();                              
		return 2;                                       
	}
	delay_us(10);
	if(sccb_bus_write_byte(regDat)==0)                    
	{
		sccb_bus_stop();                                 
		return 3;
	}
	sccb_bus_stop();                                    
	return 0;
}


unsigned char ArduCAM:: rdSensorReg8_8(unsigned char regID, unsigned char* regDat)
{
	delay_us(10);
	
	sccb_bus_start();
	if(sccb_bus_write_byte(sensor_addr) == 0)                 
	{
		sccb_bus_stop();                                
		//goto start;
		return 1;                                        
	}
	delay_us(10);
	if(sccb_bus_write_byte(regID)==0)//ID
	{
		sccb_bus_stop();                                  
		//goto start;
		return 2;                                       
	}
	sccb_bus_stop();                                   
	delay_us(10);	
	sccb_bus_start();
	if(sccb_bus_write_byte(sensor_addr|0x01)==0)                    
	{
		sccb_bus_stop();                                   
		//goto start;
		return 3;                                          
	}
	delay_us(10);
	*regDat = sccb_bus_read_byte();                    
	sccb_bus_send_noack();                                
	sccb_bus_stop();                                      
	return 0;                
}

//I2C Array Write 8bit address, 8bit data
int ArduCAM:: wrSensorRegs8_8(const struct sensor_reg reglist[])
{
  int err = 0;
  unsigned int reg_addr = 0;
  unsigned int reg_val = 0;
  const struct sensor_reg *next = reglist;
  while ((reg_addr != 0xff) | (reg_val != 0xff))
  {
    reg_addr =next->reg;
    reg_val = next->val;
    err = wrSensorReg8_8(reg_addr, reg_val);
    delay_ms(10);
    next++;
  }

  return err;
}

unsigned char ArduCAM:: wrSensorReg16_8(int regID, int regDat)
{
  write_reg(0X0B,regID >> 8);
  write_reg(0X0C,regID & 0XFF);
  write_reg(0X0D,regDat);
  delay_ms(1);
  return(1);
}

int ArduCAM:: wrSensorRegs16_8(const struct sensor_reg reglist[])
{
  int err = 0;
  unsigned int reg_addr;
  unsigned char reg_val;
  const struct sensor_reg *next = reglist;

  while ((reg_addr != 0xffff) | (reg_val != 0xff))
  {
    reg_addr =next->reg;
    reg_val = next->val;
    err = wrSensorReg16_8(reg_addr, reg_val);
    next++;
	delay_ms(1);
  }
  return err;
}

int ArduCAM:: rdSensorRegs16_8(const struct sensor_reg reglist[])
{
  int err = 0;
  unsigned char testVal =0;
  unsigned int reg_addr;
  unsigned char reg_val;
  const struct sensor_reg *next = reglist;

  while ((reg_addr != 0xffff) | (reg_val != 0xff))
  {
    reg_addr =next->reg;
    reg_val = next->val;
   // err = wrSensorReg16_8(reg_addr, reg_val);
		//printf("Write register %04x value %02x\r\n",reg_addr,reg_val);
		rdSensorReg16_8(reg_addr,&testVal);
		printf("Read  register %04x value %02x  ",reg_addr,testVal);
		if(testVal != reg_val){
			printf("(error) \r\n");
		}else{
		printf("\r\n");
		}
    next++;
  }
  return err;
}

unsigned char ArduCAM:: rdSensorReg16_8(unsigned int regID, unsigned char* regDat)
{
  write_reg(0X0B,regID >> 8);
  write_reg(0X0C,regID & 0XFF);
  write_reg(0X07, 0X01);
  delay_ms(1);
  *regDat = read_reg(0X4A);
  delay_ms(1);
  return(1);
}

void ArduCAM:: resetFirmware(){
    //Reset the CPLD
    write_reg(0x07, 0x80);
    delay_ms(100);
    write_reg(0x07, 0x00);
    delay_ms(100);

}


void ArduCAM:: Arducam_bus_detect(void){
    uint8_t temp;
	 while(1){	 
		 write_reg(ARDUCHIP_TEST1, 0x55  );
		 temp = read_reg(ARDUCHIP_TEST1  );
		 if (temp != 0x55){
			 printf("SPI interface Error!\n");
			 delay_ms(1000);
			 continue;
		 }
		 
		 else{
			  printf("SPIinterface OK!\r\n");
			 break;
		 }
	 }	 
}

void ArduCAM::IMX225_set_RAW_size(uint8_t size)
{
    write_reg(0x05, 0x00);
    write_reg(0x0A, 0x34);
    write_reg(0x0E, 0x0f);// Number of rows cropped above
    write_reg(0x0F, 0x00);
    write_reg(0x10, 0x00);
    switch(size)
    {
        case IMX225_640x480:
            wrSensorRegs16_8(IMX225_RAW_640x480);
            delay_ms(200);
            break;
        case IMX225_1280x960:
            wrSensorRegs16_8(IMX225_RAW_1280x960);
            delay_ms(200);
            break;
        case IMX225_BINNING:
            wrSensorRegs16_8(IMX225_binning);
            delay_ms(200);
            break;
        default:
            wrSensorRegs16_8(IMX225_960p);
            delay_ms(200);
            break;
    }
}

uint16_t ArduCAM::read_resolution_column(void)
{
	uint16_t data;
	
	uint16_t col_l = bus_read(COLUMN_LOW_RESO);
	uint16_t col_h = bus_read(COLUMN_HIGH_RESO);
	data = (col_h << 8) | col_l;
	
	return data;
}

uint16_t ArduCAM::read_resolution_row(void)
{
	uint16_t data;
	
	uint16_t row_l = bus_read(ROW_LOW_RESO);
	uint16_t row_h = bus_read(ROW_HIGH_RESO);
	data = (row_h << 8) | row_l;
	
	return data;
}

uint8_t* ArduCAM::read_trace_id(void)
{	
	trace_id_data[7] = bus_read(TRACE_ID_8);
	trace_id_data[6] = bus_read(TRACE_ID_7);
	trace_id_data[5] = bus_read(TRACE_ID_6);
	trace_id_data[4] = bus_read(TRACE_ID_5);
	trace_id_data[3] = bus_read(TRACE_ID_4);
	trace_id_data[2] = bus_read(TRACE_ID_3);
	trace_id_data[1] = bus_read(TRACE_ID_2);
	trace_id_data[0] = bus_read(TRACE_ID_1);
	
	return trace_id_data;
}

void ArduCAM::sensor_power_down(void)//problem
{
    write_reg(GPIO_WRITE, 0x02 | read_reg(GPIO_WRITE));   
}

void ArduCAM::sensor_power_enable(void)//problem
{
    write_reg(GPIO_WRITE, read_reg(GPIO_WRITE) & ~(1 << 1));
    write_reg(GPIO_WRITE, 0x04 | read_reg(GPIO_WRITE));   
}

void ArduCAM::IMX225_sensor_standby(void)
{
    wrSensorReg16_8(0x3000, 0x01);    
}

void ArduCAM::IMX225_sensor_on(void)
{
    wrSensorReg16_8(0x3000, 0x00);    
}

void ArduCAM::IMX225_gain_conversion_mode(uint8_t mode)
{
    uint8_t temp;
    rdSensorReg16_8(0x3009 , &temp);
    temp = temp&~(1 << 4);
    if(mode == HCG)
        temp = temp|(1 << 4);
    wrSensorReg16_8(0x3009, temp);      
}

void ArduCAM::IMX225_set_gain(float val)
{
    uint16_t temp = val*10;
    uint8_t gain_lsb = temp & 0xff;     //get LSB val
    uint8_t gain_msb = (temp >> 8) & 0x03;  //get MSB val
    wrSensorReg16_8(0x3015, gain_msb);
    wrSensorReg16_8(0x3014, gain_lsb);  
}

void ArduCAM::IMX225_normal_exposure(uint16_t val)
{
    uint8_t shs1_l = val & 0xff;     
    uint8_t shs1_h = (val >> 8) & 0xff;  
    wrSensorReg16_8(0x3021, shs1_h);
    wrSensorReg16_8(0x3020, shs1_l);  
}

void ArduCAM::IMX225_long_exposure(uint16_t val)
{
    uint8_t vmax_l = val & 0xff;     
    uint8_t vmax_h = (val >> 8) & 0xff;  
    wrSensorReg16_8(0x3019, vmax_h);
    wrSensorReg16_8(0x3018, vmax_l);  
}

void ArduCAM::IMX225_vertical_inversion_control(uint8_t mode)
{
    uint8_t temp;
    rdSensorReg16_8(0x3007 , &temp);
    temp = temp&~(1 << 0);
    if(mode == INVERTED)
        temp = temp|1;
    wrSensorReg16_8(0x3007, temp);   
}

void ArduCAM::IMX225_horizontal_inversion_control(uint8_t mode)
{
    uint8_t temp;
    rdSensorReg16_8(0x3007 , &temp);
    temp = temp&~(1 << 1);
    if(mode == INVERTED)
        temp = temp|(1 << 1);
    wrSensorReg16_8(0x3007, temp);   
}

void ArduCAM::IMX225_exposure(uint16_t val)
{
    uint32_t _val = 33 * val;
    uint8_t shs1_1;
    uint8_t shs1_2;
    uint8_t shs1_3;
    uint8_t vmax_1;
    uint8_t vmax_2;
    uint8_t vmax_3;
    if (_val <= 1097)
    {
        vmax_1 = 0x4c;
        vmax_2 = 0x04;
        vmax_3 = 0x00;
        _val = 1099 - _val;
        shs1_1 = _val & 0xff;
        shs1_2 = (_val >> 8) & 0xff;
        shs1_3 = (_val >> 16) & 0xff;
    }
    else if (_val > 1097)
    {
        shs1_1 = 0x02;
        shs1_2 = 0x00;
        shs1_3 = 0x00;
        _val = _val + 3;
        vmax_1 = _val & 0xff;
        vmax_2 = (_val >> 8) & 0xff;
        vmax_3 = (_val >> 16) & 0xff;
    }
    wrSensorReg16_8(0x3018, vmax_1);
    wrSensorReg16_8(0x3019, vmax_2);
    wrSensorReg16_8(0x301a, vmax_3);
    wrSensorReg16_8(0x3020, shs1_1);
    wrSensorReg16_8(0x3021, shs1_2);
    wrSensorReg16_8(0x3022, shs1_3);
}

