from client_lib import GetStatus,GetRaw,GetSeg,AVControl,CloseSocket
import cv2
import numpy as np
import math

brake = 0
def AngCal(image):
    global brake
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = (gray*(255/max(np.max(gray),0.001))).astype(np.uint8)
    cv2.imshow("test", gray)
    h, w = gray.shape

    
    arr = []

    for CHECKPOINT in range(160, 92, -33):

        line_row = gray[CHECKPOINT, :]
        # print(line_row)
        # gray = cv2.line(gray, (0, CHECKPOINT), (w-1, CHECKPOINT), 90, 2)
        # cv2.imshow('test', gray)

        flag = True
        min_x = 0
        max_x = 0
        
        for x, y in enumerate(line_row):
            if y == 255 and flag:
                flag = False
                min_x = x
            elif y == 255:
                max_x = x

        center_row = int((max_x+min_x)/2)
        arr.append(center_row)
        gray = cv2.circle(gray, (center_row, CHECKPOINT), 1, 90, 2)
        cv2.imshow('test', gray)
    

    x0, y0 = int(w/2), h
    gray = cv2.circle(gray, (x0, 180), 1, 90, 2)
    cv2.imshow('test', gray)
    steer_point = arr[0]
    if abs(arr[2] - x0) == x0 and abs(arr[1] - x0) >= 4/5* x0 and abs(arr[0] - x0) >= x0*4/5:
        max_speed = -90
        max_angle = 25
    elif abs(arr[2] - x0) > x0*2/3 and abs(arr[1] - x0) > x0*1/3:
        max_angle = 25
        if brake > 0:
            brake = brake - 1
            max_speed = 0
        else:
            max_speed = 27
    elif abs(arr[2] - x0) > x0*1/4:
        max_angle = 10
        if brake > 0:
            brake = brake - 1
            max_speed = 0
        else:
            max_speed = 30
    else:
        if brake < 9:
            brake = brake + 1
        max_angle = 1
        max_speed = 60
        steer_point = arr[2]

    
    x1, y1 = steer_point, CHECKPOINT


    value = (x1-x0)/(y0-y1)
    angle = math.degrees(math.atan(value))
    # print(steering)
        
    if angle > max_angle:
        angle = max_angle
    elif angle < -max_angle:
        angle = -max_angle

    
    print(max_speed, angle)
    
    return angle, max_speed


if __name__ == "__main__":
    try:
        sum = 0
        count = 0
        while True:
            state = GetStatus()
            raw_image = GetRaw()
            segment_image = GetSeg()
            # print(segment_image.shape)

            print(state)
            # cv2.imshow('raw_image', raw_image)
            # cv2.imshow('segment_image', segment_image)

            angle, speed = AngCal(segment_image)
            # print(math.degrees(angle))
            AVControl(speed, angle)
            sum = sum + speed
            count = count + 1

            key = cv2.waitKey(1)
            if key == ord('q'):
                break
        
    finally:
        sum = sum / count
        print('closing socket')
        print('avg speed: ', sum)
        CloseSocket()
