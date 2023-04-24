import sensor, image, time, pyb
import math
from pyb import UART, Timer

# 返回参数初始化
tube_offset_angle = 0                               # 管道偏移角
tube_offset_distance = 0                            # 管道偏移距离
obstacle_shape = 0                                  # 障碍物形状，取值规则：0:没有障碍物；1:圆形障碍物；2:矩形障碍物
# 调试参数
tube_threshold = (30, 100, -128, 127, -128, 127)     # 管道LAB阈值
obstacle_threshold = (0, 18, -7, 26, -3, 12)    # 障碍物LAB阈值
timer_freg = 25                                     # 定时器触发间隔（Hz）

# 定时器回调函数
def timeFunc(timer):
    time_flag = 1

# 判断障碍块位置
# return: 0:left 1:center 2:right 3:error
def getPosition(o_b, t_b):
    # 计算与管道中心的偏移
    x_offset = (o_b[0] + o_b[2]/2) - (t_b[0] + t_b[2]/2)
#    print(x_offset)
    if abs(x_offset) < ((75 / scale)/5):
        p_flag = 1
    elif x_offset < 0:
        p_flag = 0
    elif x_offset > 0:
        p_flag = 2
    else:
        p_flag = 3
#    print(p_flag)
    return p_flag

def find_max(blobs):
    max_size=0
    for blob in blobs:
        # if blob.pixels()>=250 and blob.pixels()<=7000:
            if blob.pixels() > max_size:
                max_blob=blob
                max_size = blob.pixels()
                return max_blob

sensor.reset()                          # 初始化摄像头
sensor.set_pixformat(sensor.RGB565)     # 格式为 RGB565
sensor.set_framesize(sensor.QQVGA)      # 使用 QQVGA 速度快一些，160*120
sensor.skip_frames(n = 800)             # 跳过800s，使新设置生效,并自动调节白平衡
sensor.set_auto_gain(False)             # 关闭自动自动增益
sensor.set_auto_whitebal(False)
uart = UART(3, 115200)                  # 初始化串口通信参数
clock = time.clock()                    # 追踪帧率
time_flag = 0                           # 定时标志位
timer = Timer(2)                        # 使用定时器2创建一个定时器对象
timer.init(freq=timer_freg)             # 设置触发间隔
timer.callback(timeFunc)                # 定义定时器回调函数
scale = 0                               # 图像比例尺(mm/pixel)

while (True):
    clock.tick()
    img = sensor.snapshot()
    # 识别管道
    tube_blobs = img.find_blobs([tube_threshold], pixels_threshold = 2000)
    if tube_blobs:
        tube_flag = 1
        t_b = find_max(tube_blobs)
        tube_offset_angle = t_b[7]
        tube_offset_distance = t_b[5]
        scale = 75 / t_b[2]
        # print(scale)
        img.draw_rectangle(t_b[0:4])
        # 绘制管道方向线
        # img.dra   w_line((t_b[5], t_b[6], t_b[5] + int(50 * math.cos(t_b[7])), t_b[6] + int(50 * math.sin(t_b[7]))),color = (255,255,255))
        # 识别障碍物
        obstacle_blobs = img.find_blobs([obstacle_threshold], roi = (t_b[0:4]), pixels_threshold = 100)
        if obstacle_blobs:
            o_b = find_max(obstacle_blobs)
            img.draw_rectangle(o_b[0:4])
            if abs((o_b[1] + o_b[3]/2)-60) < 30*scale:
                # 判断位置
                # img.draw_line(int(o_b[0] + o_b[2]/2),0,int(o_b[0] + o_b[2]/2),120,color = (255,0,0))
                # img.draw_line(int(t_b[0] + t_b[2]/2),0,int(t_b[0] + t_b[2]/2),120,color = (255,0,0))
                p = getPosition(o_b, t_b)
                # 障碍块在中间
                if p == 1:
                    circles = img.find_circles(roi = t_b.rect(),threshold = 3000, x_margin = 10, y_margin = 10, r_margin = 10,
                    r_min = int(10*scale), r_max = int(30*scale))
                    if circles:
                        for c in circles:
                            # img.draw_circle(c.x(),c.y(),c.r())
                            obstacle_shape = 1
                    else:
                        obstacle_shape = 2
                # 障碍块在左侧或者右侧，判断方法相同
                elif p == 0 or p == 2:
                    if o_b[3] > 35*scale:
                        # print(o_b[3] - 35*scale)
                        obstacle_shape = 2
                    else:
                        # print(o_b.density())
                        if o_b.density() < 0.85:
                            obstacle_shape = 1
                        else:
                            obstacle_shape = 2
                # 出错
                else:
                    pass
            else:
                obstacle_shape = 0
        else:
            obstacle_shape = 0
    else:
        tube_flag = 0
        tube_offset_distance = 0
        tube_offset_angle = 0

    # 串口通信
    if time_flag == 0:
        uart.write('D%03dA%03dS%01dE' % (tube_offset_distance, tube_offset_angle * 53, obstacle_shape))
        print('D%03dA%03dS%01dE' % (tube_offset_distance, tube_offset_angle * 53, obstacle_shape))
        time_flag = 0
    # 打印帧率
    print(clock.fps())
