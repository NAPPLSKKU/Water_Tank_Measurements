#include <iostream>
#include <string>
#include "ArduCAM.h"
#include <unistd.h>
#include <fstream>
#include <pthread.h>
#include <time.h>

using namespace std;

ArduCAM myCAM(IMX225, CAM_CS1);
pthread_mutex_t calculating = PTHREAD_MUTEX_INITIALIZER;
pthread_cond_t done = PTHREAD_COND_INITIALIZER;

float set_gain;
int set_exposure;


// Setting capturing registers: Gain & Exposure
void gain_setting(float gain_val) 
{
    if (gain_val < 0.0 || gain_val > 72.0)
    {
        cout << "Gain Value is out of range." << endl;
        return;
    }
    myCAM.IMX225_set_gain(gain_val);
}

void exp_time_setting(int exp_time_val) // Always integer
{
    if (exp_time_val < 1 || exp_time_val > 3800)
    {
        cout << "Exposure time is out of range." << endl;
        return;
    }
    myCAM.IMX225_exposure(exp_time_val);
}

void verify_registers()
{
    unsigned char gain_lsb = 0;
    unsigned char gain_msb = 0;
    unsigned char vmax_l = 0, vmax_m = 0, vmax_h = 0;

    myCAM.rdSensorReg16_8(0x3014, &gain_lsb);
    myCAM.rdSensorReg16_8(0x3015, &gain_msb);
    myCAM.rdSensorReg16_8(0x3018, &vmax_l);
    myCAM.rdSensorReg16_8(0x3019, &vmax_m);
    myCAM.rdSensorReg16_8(0x301a, &vmax_h);

    //cout << "[GAIN] MSB: 0x" << hex << (int)gain_msb << " LSB: 0x" << hex << (int)gain_lsb << endl;
    //cout << "[EXPOSURE] VMAX MSB: 0x" << hex << (int)vmax_h << " MID: 0x" << hex << (int)vmax_m << " LSB: 0x" << hex << (int)vmax_l << endl;
}

// Saving image
void myCAMSaveToSDFile(string raw_filename)
{
    myCAM.flush_fifo();
    myCAM.clear_fifo_flag();

    cout << "Start Capture" << endl;

    myCAM.start_capture();
    while (!myCAM.get_bit(ARDUCHIP_TRIG, CAP_DONE_MASK));

    cout << "Capture Done." << endl; 

    unsigned int length = myCAM.read_fifo_length();
    if (length == 0)
    {
        cout << "Capture size is 0. Aborting save." << endl;
        return;
    }

    FILE *outFile = fopen(raw_filename.c_str(), "w+");
    if (!outFile)
    {
        cout << "Error: cannot open file for writing." << endl;
        return;
    }

    myCAM.CS_LOW();
    myCAM.set_fifo_burst();
    for (unsigned int i = 0; i < length; i++)
    {
        unsigned char VL = myCAM.SPI_transfer(0x00);
        fwrite(&VL, 1, 1, outFile);
    }
    myCAM.CS_HIGH();
    fclose(outFile);
    cout << "Image saved to: " << raw_filename << endl;
}

void* capture_thread(void* arg)
{
    string raw_filename = *(static_cast<string*>(arg));

    #define SPI_CLK_SPEED 10000000
    pioInit();
    spiInit(SPI_CLK_SPEED, 0);
    myCAM.ArduCAM_Camera_ON();
    myCAM.Arducam_CS_Init();
    myCAM.resetFirmware();
    myCAM.InitCAM();

    gain_setting(set_gain);
    exp_time_setting(set_exposure);

    verify_registers();
    myCAMSaveToSDFile(raw_filename);

    myCAM.ArduCAM_Camera_OFF();

    pthread_mutex_lock(&calculating);
    pthread_cond_signal(&done);
    pthread_mutex_unlock(&calculating);

    return nullptr;
}

int main(int argc, char* argv[])
{
    setvbuf(stdout, NULL, _IONBF, 0);

    if (argc < 4)
    {
        cout << "Usage: ./simple_capturing <raw_filename> <gain> <exposure>" << endl;
        return 1;
    }

    string raw_filename = argv[1];
    set_gain = stof(argv[2]);
    set_exposure = stoi(argv[3]);

    struct timespec abs_time;
    pthread_t tid;

    pthread_mutex_lock(&calculating);
    clock_gettime(CLOCK_REALTIME, &abs_time);
    abs_time.tv_sec += 20; 

    pthread_create(&tid, NULL, capture_thread, &raw_filename);

    int err = pthread_cond_timedwait(&done, &calculating, &abs_time);
    if (err == ETIMEDOUT)
    {
        cerr << "Capture timed out!" << endl;
        return 1;
    }
    pthread_mutex_unlock(&calculating);
    pthread_join(tid, NULL);

    return 0;
}

