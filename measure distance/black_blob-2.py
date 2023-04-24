#@brief: 异物定位算法
#@date ： 2020.10.18


import sensor, image, time, math
import struct
from pyb import UART

threshold_index = 0 # 0 for red, 1 for green, 2 for blue


thresholds = [(5, 28, -23, 31, -41, 7)]

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.skip_frames(time = 2000)
sensor.set_auto_gain(False) # must be turned off for color tracking
sensor.set_auto_whitebal(False) # must be turned off for color tracking
clock = time.clock()

uart =UART(3, 115200)  #串口3，波特率115200
uart.init(115200, bits=8, parity=None, stop=1)  #8位数据位，无校验位，1位停止

def send_data_packet(x, y, l):
    temp = struct.pack("<bbfff",                #格式为俩个字符俩个整型
                   0xAA,                       #帧头1
                   0xAE,                       #帧头2
                   float(x),                   #x偏移
                   float(y),                  #y偏移
                   float(l))                    #距离
    uart.write(temp+'\r\n')                           #串口发送



K = 5000
while(True):
    clock.tick()
    img = sensor.snapshot()
    for blob in img.find_blobs([thresholds[threshold_index]], pixels_threshold=200, area_threshold=200, merge=True):

        img.draw_rectangle(blob.rect())
        img.draw_cross(blob.cx(), blob.cy())
        Lm = (blob[2]+blob[3])/2
        length = K/Lm
        send_data_packet(blob[5], blob[6], length)
    print(length)
    print(blob[5], blob[6])
