#THRESHOLD = (30, 100, -40, 50, -20, 30)
THRESHOLD=(89, 49, -8, 21, 38, 9)
import sensor, image, time
from pyb import LED
import car
from pid import PID
from pyb import UART
import ustruct
import sensor, image, time,math,pyb
from pyb import UART,LED
import json
import ustruct

rho_pid = PID(p=0.4, i=0)
theta_pid = PID(p=0.001, i=0)
LED(1).on()
LED(2).on()
LED(3).on()
sensor.reset()
sensor.set_vflip(True)
sensor.set_hmirror(True)
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQQVGA)
sensor.set_brightness(-3)
sensor.skip_frames(time = 2000)
clock = time.clock()
sensor.set_auto_gain(False)
sensor.set_auto_whitebal(False)
uart=UART(1,115200)
uart.init(115200,bits=8,parity=None,stop=1)
#def send_data(a, b, c):
    #data = ustruct.pack('<3f', a, b ,c)
    #length = ustruct.pack('<L', len(data))
    #data = b'\x0A\x0D' + data + b'\x0D\x0A'#\n\t的意思
    #uart.write(length)
    #uart.write(data)
    #time.sleep_ms(100)

def send_data(a,b,c):
    global uart
    data=ustruct.pack("<bbfffb",
                      0x2C,
                      0x12,
                      float(a),
                      float(b),
                      float(c),
                      0x5B)
    print('success')
    uart.write(data);
    time.sleep_ms(100)

while(True):
    clock.tick()
    img = sensor.snapshot().binary([THRESHOLD])
    blobs = img.find_blobs([THRESHOLD], pixel_threshold=200, area_threshold=200, merge=True)
    largest_blob = None
    max_pixels = 0

    for b in blobs:
        if b.pixels() > max_pixels:
            largest_blob = b
            max_pixels = b.pixels()
    if largest_blob is not None:
        pixels = largest_blob.pixels()
        if pixels < 1200:
            print("-1213 %d -1"%pixels)#下降状态
            send_data(-1213,-1, pixels)
        elif pixels > 1900:
            print("-1213 %d 1"%pixels)#上升状态
            send_data(-1213, 1, pixels)
        else:
            print("-1213 %d 0"%pixels)#水平状态
            send_data(-1213, 0, pixels)
        img.draw_rectangle(largest_blob.rect())
        time.sleep_ms(100)

    line = img.get_regression([(100,100)], robust = True)#二值法巡线
    #线性回归
    if (line):
        rho_err = abs(line.rho())-img.width()/2
        if line.theta()>90:
            theta_err = line.theta()-180
        else:
            theta_err = line.theta()
        img.draw_line(line.line(), color = 127)
        if line.magnitude()>8:
            rho_output = rho_pid.get_pid(rho_err,1)
            theta_output = theta_pid.get_pid(theta_err,1)
            output = rho_output+theta_output
            outputs=30+output
            if outputs>40:
                outputs=40
            elif outputs<20:
                outputs=20
            car.run(30+output, 30-output)
            print(-1444, 30+output, 30-output)
            send_data(-1444, outputs, outputs)


    else:
        car.run(30,-30)
        send_data(-1444, 30,-30)
        print(-1444, 30,-30)
        pass
