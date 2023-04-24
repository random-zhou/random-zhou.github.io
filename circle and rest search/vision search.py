import sensor, image, time
import ustruct
from pyb import UART,LED
import sensor, image, time,math,pyb
import sensor, image, time
from pyb import LED

from pid import PID
from pyb import UART
import ustruct
import sensor, image, time,math,pyb
import sensor, image, time,math,pyb
from pyb import UART,LED            ###串口要用
import json
import ustruct
# 设定颜色阈值范围
green_threshold=(38, 0, -14, 4, 28, -1)
#green_threshold = (0, 52, -18, -5, 1, 17)#rect(38, 0, -14, 4, 28, -1)
#red_threshold = (0, 50, -19, -8, -2, 16)#circle(32, 0, -14, 16, 33, -1)
red_threshold=(32, 0, -14, 16, 33, -1)
#blue_threshold
#blue_threshold
#green_threshold=(4, 31, -15, 6, 11, -7)
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QQVGA)
sensor.skip_frames(time=2000)
clock = time.clock()

# 检测到矩形的计数器
rect_count = 0
# 最近一次检测到矩形的时间
last_rect_time = 0

# 检测到圆形的计数器
circle_count = 0.
# 最近一次检测到圆形的时间
last_circle_time = 0

#检测到三角形的计数器
triangle_count=0
#最近一次检测到三角形的时间
last_triangle=0

a = 0
b = 0

uart=UART(3,115200)
uart.init(115200,bits=8,parity=None,stop=1)

def send_data(a):
    # 将浮点数打包为字节数组
    data = ustruct.pack('<f', a)
    # 计算数据长度
    length = ustruct.pack('<L', len(data))
    # 添加帧头和帧尾
    data = b'\x0A\x0D' + data + b'\x0D\x0A'
    # 发送数据长度
    uart.write(length)
    # 发送数据
    uart.write(data)
    # time.sleep_ms()

def send_dataone():
    global uart
    data=ustruct.pack("<bbbb",
                      0x2C,
                      0x12,
                      0x01,
                      0x5B)
    print('0x01')
    uart.write(data);
    #time.sleep_ms(10)

def send_datatwo():
    global uart
    data=ustruct.pack("<bbbb",
                      0x2C,
                      0x12,
                      0x02,
                      0x5B)
    print('0x02')
    uart.write(data);
    #time.sleep_ms(10)

def send_datathree():
    global uart
    data=ustruct.pack("<bbbb",
                      0x2C,
                      0x12,
                      0x03,
                      0x5B)
    print('0x02')
    uart.write(data);
    #time.sleep_ms(10)


def send_datazero():
    global uart
    data=ustruct.pack("<bbbb",
                      0x2C,
                      0x12,
                      0x00,
                      0x5B)
    print('0x00')
    uart.write(data);
    #time.sleep_ms(100)


while True:
    clock.tick()

    img = sensor.snapshot()

    # 使用默认参数和绿色阈值检测矩形
    for r in img.find_rects(threshold=20000, roi=(0, 0, img.width(), img.height()), \
                            x_stride=2, y_stride=2, \
                            area_threshold=1000, merge=True, \
                            margin=100, \
                            robust=True, \
                            threshold_cb=None, \
                            rect_cb=None, \
                            upscale=1, \
                            pixel_threshold=20, \
                            col_threshold=20, \
                            row_threshold=20, \
                            green_threshold=green_threshold):

        # 绘制矩形并记录最后一次检测到矩形的时间
        img.draw_rectangle(r.rect(), color=(255, 0, 0))
        last_rect_time = time.ticks_ms()

        # 如果检测到矩形，则将 rect_count 计数器加 1
        rect_count += 1

        # 如果在0.3秒内检测到5个或以上的矩形，则打印1并重置 rect_count 和 last_rect_time
        if rect_count >= 3 and time.ticks_diff(time.ticks_ms(), last_rect_time) <= 300:
            a += 1

            if a == 2:
                print(2, a)
                send_datatwo()
                send_datazero()
                pyb.delay(500)
                a = 0
            rect_count = 0
            last_rect_time = 0


    # 如果距离最后一次检测到矩形的时间
    #超过0.3秒，则重置 rect_count 和 last_rect_time
    if time.ticks_diff(time.ticks_ms(), last_rect_time) >= 300:
        rect_count = 0
        last_rect_time = 0

    # 使用红色阈值范围检测圆形
    circles = img.find_circles(threshold=3250, x_margin=5, y_margin=5, r_margin=10,
                               r_min=2, r_max=50, r_step=1, roi=(0,0,160,120),thresholds=red_threshold)
    if len(circles) > 0:
        for c in circles:
            img.draw_circle(c.x(), c.y(), c.r(), color=(255, 0, 0))

        # 如果检测到圆形，则将 circle_count 计数器加1，并记录最后一次检测到圆形的时间
        circle_count += 1
        last_circle_time = time.ticks_ms()

        # 如果在0.3秒内检测到3个或以上的圆形，则打印1并重置 circle_count 和 last_circle_time
        if circle_count >= 5 and time.ticks_diff(time.ticks_ms(), last_circle_time) <= 300:
            b += 1
            if b == 2:
                print(3, b)
                send_dataone()
                pyb.delay(200)
                send_datazero()


                b = 0
            circle_count = 0
            last_circle_time = 0
        #else:
            #send_datazero()


    # 如果距离最后一次检测到圆形的时间超过0.3秒，则重置 circle_count 和 last_circle_time
    if time.ticks_diff(time.ticks_ms(), last_circle_time) >= 300:
        circle_count = 0
        last_circle_time = 0

    if rect_count == 0 and circle_count == 0:
        c=1
        # print(1)
        # send_data(1)
    #print(clock.fps())
