from client_lib import GetStatus,GetRaw,GetSeg,AVControl,CloseSocket
import cv2
import numpy as np
import math

brake = 0
brake1 = 0
right_accumulator = 0
left_accumulator = 8
turn_count = 0
turn_flag = 1
def ComputeAngle(steer_point,steer_height):
    global right_accumulator
    global left_accumulator
    x1, y1 = steer_point, steer_height
    x0, y0 = 160, 180
    value = (x1-x0)/(y0-y1)
    angle = math.degrees(math.atan(value))
    if angle >= 1 and angle <= 15:
        if right_accumulator < 6:
            right_accumulator = right_accumulator + 1

        angle = angle*0.005

    elif angle <= -1 and angle >= -15:
        if left_accumulator < 6:
            left_accumulator = left_accumulator + 1

        angle = angle*0.005

    if angle > 15 and left_accumulator > 0:
        angle = angle*0.1
        left_accumulator = left_accumulator-1
    elif angle < -15 and right_accumulator > 0:
        angle = angle*0.1
        right_accumulator = right_accumulator-1
    return angle

def AngCal(image):
    global brake
    global brake1
    global turn_count
    global turn_flag
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = (gray*(255/max(np.max(gray),0.001))).astype(np.uint8)
    cv2.imshow("test", gray)
    h, w = gray.shape

    
    arr = []

    for CHECKPOINT in range(160, 92, -30):

        line_row = gray[CHECKPOINT, :]
        # print(line_row)
        # gray = cv2.line(gray, (0, CHECKPOINT), (w-1, CHECKPOINT), 90, 2)
        # cv2.imshow('test', gray)

        flag = True
        min_x = 0
        max_x = 0
        first_white = False
        for x, y in enumerate(line_row):
            if y == 255 and flag:
                flag = False
                min_x = x
                if x < w*0.1 and CHECKPOINT == 160-33:
                    first_white = True
            elif y == 255:
                max_x = x

            center_row = int(min_x + (max_x-min_x)*0.5)
            #Change steer point position
            if CHECKPOINT == 160:
                center_row = int(min_x + (max_x - min_x)*0.6)
            if CHECKPOINT < 100: 
                center_row = int(min_x + (max_x - min_x)*0.85)
        arr.append(center_row)
        gray = cv2.circle(gray, (center_row, CHECKPOINT), 1, 90, 2)
        cv2.imshow('test', gray)
    

    x0, y0 = int(w/2), h
    gray = cv2.circle(gray, (x0, 180), 1, 90, 2)
    cv2.imshow('test', gray)
    if first_white:
        steer_point = arr[0]*0.45
    else:
        steer_point = arr[0]
    steer_height = 94
    if abs(arr[2] - x0) == x0 and abs(arr[1] - x0) >= 4/5* x0 and abs(arr[0] - x0) >= x0*1/2:
        max_speed = -10
        if turn_count < 8 and turn_flag == 1:
            max_angle = 25
            turn_count = turn_count + 1
        else:
            max_angle = 0
            turn_count = 0
            turn_flag = 0
    # elif abs(arr[2] - x0) < x0*0.4 and abs(arr[2] - arr[1]) < x0*0.2 and abs(arr[1] - arr[0]) < x0*0.2:
    #     turn_flag = 1
    #     max_angle = 0.3
    #     if brake < 9:
    #         brake = brake + 1
    #     max_speed = 60
    #     steer_point = arr[2]
    elif abs(arr[2] - x0) < x0*1/2 or abs(arr[1] - x0) < x0*0.24:
        turn_flag = 1
        turn_count = 0
        max_angle = 6
        # if brake > 0:
        #     brake = brake - 1
        #     max_speed = 0
        #     max_angle = 1
        # else:
        max_speed = 40
        if brake1 < 3:
            brake1 = brake1 + 1
    else:
        turn_flag = 1
        turn_count = 0
        max_angle = 15
        # if brake > 0:
        #     brake = brake - 1
        #     max_speed = 0
        #     max_angle = 1
        if brake1 > 0:
            brake1 = brake1 - 1
            max_speed = 0
            # max_angle = 1
        else:
            max_speed = 25
            # brake = brake + 1

    

    
    angle = ComputeAngle(steer_point, steer_height)



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
            # raw_image = GetRaw()
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
