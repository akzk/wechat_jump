import os
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import math
import time
import random

coef1 = 1.48
coef2 = 1.43
coef3 = 1.39

coef = coef1

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

    return get_point_with_diff_color(img, start_x, start_y, end_x, img.shape[0], ignore_x=(start_point_x-100, start_point_x+100))

def find_target_bottom_point(img, top_point):

    return get_point_with_diff_color(img, top_point[1], top_point[0]+1, top_point[1]+1, img.shape[0])

def find_chess_point(img, y_start, y_end):
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

def find_start_point(img):
    return find_chess_point(img, 1000, 1500)

def find_actual_drop_point(img, target_y):
    return find_chess_point(img, target_y-100, target_y+100)
    

def get_screenshot():

    if os.path.exists("/Users/leonardo/Desktop/tmp2.png"):
        os.rename("/Users/leonardo/Desktop/tmp2.png", "/Users/leonardo/Desktop/tmp3.png")
    if os.path.exists("/Users/leonardo/Desktop/tmp.png"):
        os.rename("/Users/leonardo/Desktop/tmp.png", "/Users/leonardo/Desktop/tmp2.png")
    os.system("adb shell screencap -p /sdcard/tmp.png")
    os.system("adb pull /sdcard/tmp.png ~/Desktop/")

def jump(distance):

    press_time = distance * coef
    press_time = max(press_time, 100)
    press_time = int(press_time)

    print("s: %d pixel, t: %d ms" % (distance, press_time))
    os.system("adb shell input swipe {x} {y} {x} {y} {duration}".format(duration=press_time, x=int(random.uniform(0, 300))+300, y=int(random.uniform(0, 300))+900))

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
        name = time.strftime('%Y%m%d-%H%M',time.localtime(time.time()))
        if os.path.exists("/Users/leonardo/Desktop/tmp2.png"):
            os.rename("/Users/leonardo/Desktop/tmp2.png", "/Users/leonardo/Desktop/jump/"+name+"-b.png")
        
        if os.path.exists("/Users/leonardo/Desktop/tmp3.png"):
            os.rename("/Users/leonardo/Desktop/tmp3.png", "/Users/leonardo/Desktop/jump/"+name+"-a.png")

        os.system("adb shell input tap 500 1600")
        time.sleep(1)

        continue

    start_point = find_start_point(img)
    if not start_point:
        break

    print("start point:", start_point)

    target_top_point = find_target_top_point(img, start_point[1])
    if not target_top_point:
        break

    x_distance = abs(start_point[1]-target_top_point[1])
    y_distance = 0.685 * x_distance

    target_point = (int(start_point[0]-y_distance), target_top_point[1])

    if target_point[0]-target_top_point[0] < 10:
        x_distance -= 20
        y_distance = 0.685 * x_distance
        target_point = (int(start_point[0]-y_distance), target_top_point[1])

    print("target point:", target_point)

    coef = coef1
    if 450 > x_distance > 250:
        coef = coef2
    elif x_distance >= 450:
        coef = coef3

    distance = math.sqrt(x_distance**2 + y_distance**2)
    print("x_d: %d pixel, y_d: %d pixel" % (x_distance, y_distance))

    jump(distance)

    time.sleep(0.3)
    os.remove("/Users/leonardo/Desktop/tmp.png")
    get_screenshot()
    img = mpimg.imread("/Users/leonardo/Desktop/tmp.png")
    actual_point = find_actual_drop_point(img, target_point[0])
    if not actual_point:
        time.sleep(3)
        continue
    
    plt.clf()
    plt.imshow(img)
    plt.plot(actual_point[1], actual_point[0], 'o')
    plt.plot([start_point[1], target_point[1]], [start_point[0], target_point[0]], color="red")
    plt.xticks([])
    plt.yticks([])
    plt.axis("off")
    plt.savefig("/Users/leonardo/Desktop/tmp.png", bbox_inches="tight")

    time.sleep(3+int(random.uniform(0, 3)))


