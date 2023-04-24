# Single Color RGB565 Blob Tracking Example
#
# This example shows off single color RGB565 tracking using the OpenMV Cam.

import sensor, image, time, math,struct
from pyb import UART
import ustruct
threshold_index = 0 # 0 for red, 1 for green, 2 for blue

thresholds = [(1, 21, -121, 127, -6, 127)] # generic_blue_thresholds

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(time = 200)
sensor.set_auto_gain(True) # must be turned off for color tracking
sensor.set_auto_whitebal(True) # must be turned off for color tracking
clock = time.clock()

uart =UART(3, 115200)  #串口3，波特率115200
uart.init(115200, bits=8, parity=None, stop=1)  #8位数据位，无校验位，1位停止位

def send_data_packet(x, y,l,s):
    temp = struct.pack("<bbffff",                #格式为俩个字符俩个整型
                   0xff,                       #帧头1
                   0x5B,                       #帧头2
                   float(x),
                   float(y),
                   float(l),
                   float(s))
    uart.write(temp)

#def sending_data(l,s):
    #global uart;
    #data=ustruct.pack("<bbfhb",
    #0x2C,
    #0x12,
    #float(l),
    #int(s),
    #0x5B)
    #uart.write(data)
    #time.sleep_ms(100)

def sending_data(x,y,l,s):
    global uart;
    data=ustruct.pack("<bbhhffb",
    0x2C,
    0x12,
    int(x),
    int(y),
    float(l),
    float(s),
    0x5B)
    uart.write(data)
    time.sleep_ms(100)

def sending_datas(x):
    global uart;
    datas=ustruct.pack("<bbh",
    0x2C,
    0x12,
    int(x))
    uart.write(datas)
    time.sleep_ms(3000)




K=5000
while(True):
    clock.tick()
    img = sensor.snapshot()
    b = img.find_blobs([thresholds[0]], pixels_threshold=200, area_threshold=200, merge=True)
    r = img.find_rects(threshold = 10000)
    c = img.find_circles(threshold = 3500, x_margin = 10, y_margin = 10, r_margin = 10,r_min = 2, r_max = 100, r_step = 2)
    if b:

        if c:
            for blob in b:
                img.draw_rectangle(blob.rect())
                img.draw_cross(blob.cx(),blob.cy())
                Lm = (blob[2] +blob[3])/2
                length = K/Lm
                #send_data_packet(blob[5], blob[6],length,2.0)
                #sending_data(length,2)
                #print(length,2)
                #sending_data(1.0,2.0,3.0,2.0)
                #sending_datas(blob[5])
                #uart.write(blob[5])
                #print(blob[5], blob[6],int(length),2)
                sending_data(blob[5],blob[6],length,2.0)
                print(blob[5], blob[6],length,2.0)
                #print(blob[5])
        else:
            for blob in b:
                img.draw_rectangle(blob.rect())
                img.draw_cross(blob.cx(),blob.cy())
                Lm = (blob[2] +blob[3])/2
                length = K/Lm
                #send_data_packet(blob[5], blob[6],length,1.0)
                sending_data(blob[5],blob[6],length,1.0)
                #sending_data(1.0,2.0,3.0,1.0)
                #sending_data(length,1)
                #print(length,1)
                #sending_datas(blob[5])
                #uart.write(blob[5])
                #print(blob[5], blob[6],int(length),1)
                print(blob[5], blob[6],length,1.0)
                #print(blob[5])
    else:
        #send_data_packet(0.0, 0.0,0.0,0.0)
        #sending_data(0,0,0,0)
        #print(0, 0,0,0)
        sending_data(0.0,0.0,0.0,0.0)
        print(0.0, 0.0,0.0,0.0)
        #FH=bytearray([])
        #uart.write(FH)

#if c:
            #for blob in b:
                #img.draw_rectangle(blob.rect())
                #img.draw_cross(blob.cx(),blob.cy())
                #Lm = (blob[2] +blob[3])/2
                #length = K/Lm
                ##send_data_packet(blob[5], blob[6],length,2.0)
                #sending_data(blob[5],blob[6],length,2.0)
                ##sending_datas(blob[5])
                ##uart.write(blob[5])
                #print(blob[5], blob[6],length,2.0)
                #print(blob[5])
        #else:
            #for blob in b:
                #img.draw_rectangle(blob.rect())
                #img.draw_cross(blob.cx(),blob.cy())
                #Lm = (blob[2] +blob[3])/2
                #length = K/Lm
                ##send_data_packet(blob[5], blob[6],length,1.0)
                #sending_data(blob[5],blob[6],length,1.0)
                ##sending_datas(blob[5])
                ##uart.write(blob[5])
                #print(blob[5], blob[6],length,1.0)
                ##print(blob[5])
    #else:
        ##send_data_packet(0.0, 0.0,0.0,0.0)
        #sending_data(0.0,0.0,0.0,0.0)
        #print(0.0, 0.0,0.0,0.0)
        ##FH=bytearray([])
        ##uart.write(FH)


