import os
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import math
import time


def get_point_with_diff_color(img, start_x, start_y, end_x, end_y, allow_range=0.1, ignore_x=(), ignore_y=()):

    for y in range(start_y, end_y):
        standard_color = img[y-1][start_x]

        for x in range(start_x, end_x):
            
            color = img[y][x]

            if len(ignore_x) > 0 and ignore_x[0] < x < ignore_x[1]:
                continue

            if len(ignore_y) > 0 and ignore_y[0] < x < ignore_y[1]:
                continue

            for i in range(3):
                if (standard_color[i]-allow_range) > color[i] or color[i] > (standard_color[i]+allow_range):
                    return (y, x)

            standard_color = color

    return False

def find_target_top_point(img, start_point_x, start_y=500, allow_range=0.1):

    if start_point_x < img.shape[1]/2:
        start_x = start_point_x + 50
        end_x = img.shape[1]-100
    else:
        start_x = 100
        end_x = start_point_x - 50

    return get_point_with_diff_color(img, start_x, start_y, end_x, img.shape[0], ignore_x=(start_point_x-60, start_point_x+60))

def find_target_bottom_point(img, top_point):

    return get_point_with_diff_color(img, top_point[1], top_point[0]+1, top_point[1]+1, img.shape[0])

def get_target_point(img, start_point_x):

    top_point = find_target_top_point(img, start_point_x)
    if not top_point:
        return False

    bottom_point = find_target_bottom_point(img, top_point)
    if not bottom_point:
        return False

    h = bottom_point[0] - top_point[0]
    if h < 30:
        h = 25
    elif h > 300:
        h = 25
    else:
        h /= 2

    return (int(top_point[0]+h), top_point[1])

def find_start_point(img, y_start=1000, y_end=1500):

    min_color=[0.20, 0.22, 0.38]
    max_color=[0.22, 0.24, 0.42]
    
    for y in range(y_end, y_start, -1):
        for x in range(100, img.shape[1]-100):

            color = img[y][x]

            isit = True
            for i in range(3):
                if min_color[i] > color[i] or color[i] > max_color[i]:
                    isit = False
                    break
            if isit:    
                return (y-20, x+10)
    
    return False

def get_screenshot():

    if os.path.exists("/Users/leonardo/Desktop/tmp2.png"):
        os.rename("/Users/leonardo/Desktop/tmp2.png", "/Users/leonardo/Desktop/tmp3.png")
    if os.path.exists("/Users/leonardo/Desktop/tmp.png"):
        os.rename("/Users/leonardo/Desktop/tmp.png", "/Users/leonardo/Desktop/tmp2.png")
    os.system("adb shell screencap -p /sdcard/tmp.png")
    os.system("adb pull /sdcard/tmp.png ~/Desktop/")

def jump(distance):

    a = 1.45

    press_time = distance * a
    press_time = max(press_time, 100)
    press_time = int(press_time)

    print("s: %d pixel, t: %d ms" % (distance, press_time))
    os.system("adb shell input swipe 500 1600 500 1600 {duration}".format(duration=press_time))

def isEnd(img):
    
    green_color = img[1600][400]
    min_color=[0.0, 0.7, 0.4]
    max_color=[0.1, 0.8, 0.5]

    for i in range(3):
        if min_color[i] > green_color[i] or max_color[i] < green_color[i]:
            return False
    
    black_color = img[1560][640]
    max_color=[0.1, 0.1, 0.1]

    for i in range(3):
        if max_color[i] < black_color[i]:
            return False
    
    return True

def show_pic():
    img = mpimg.imread("/Users/leonardo/Desktop/tmp.png")
    print(img[100][100])
    plt.imshow(img)
    plt.show()


# show_pic()
# exit()

while 1:

    get_screenshot()
    img = mpimg.imread("/Users/leonardo/Desktop/tmp.png")

    if isEnd(img):
        if os.path.exists("/Users/leonardo/Desktop/tmp2.png"):
            name = time.strftime('%Y%m%d-%H%M.png',time.localtime(time.time()))
            os.rename("/Users/leonardo/Desktop/tmp2.png", "/Users/leonardo/Desktop/jump/"+name+"-a")
        
        if os.path.exists("/Users/leonardo/Desktop/tmp2.png"):
            name = time.strftime('%Y%m%d-%H%M.png',time.localtime(time.time()))
            os.rename("/Users/leonardo/Desktop/tmp2.png", "/Users/leonardo/Desktop/jump/"+name+"-b")

        os.system("adb shell input tap 500 1600")
        time.sleep(1)

        continue

    start_point = find_start_point(img)
    if not start_point:
        break

    print("start point:", start_point)

    target_point = get_target_point(img, start_point[1])
    if not target_point:
        break

    print("target point:", target_point)

    # plt.imshow(img)
    # plt.plot([start_point[1], target_point[1]], [start_point[0], target_point[0]])
    # plt.savefig("/Users/leonardo/Desktop/tmp.png")
    # exit()

    x_distance = abs(start_point[0]-target_point[0])
    y_distance = abs(start_point[1]-target_point[1])

    distance = math.sqrt(x_distance**2 + y_distance**2)
    print("x_d: %d pixel, y_d: %d pixel" % (x_distance, y_distance))

    jump(distance)
    time.sleep(3)


