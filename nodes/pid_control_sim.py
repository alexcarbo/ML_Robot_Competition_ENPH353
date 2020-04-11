#!/usr/bin/env python
import rospy
from std_msgs.msg import String
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
import cv2
import numpy as np
import roslib
import sys

from cv_bridge import CvBridge, CvBridgeError
import time
import math
import constants as const


class LineFollower:
    def __init__(self):
        self.prev_error = 0
        self.count = 0
        self.angle = -80
        self.ignore_next = False
        self.ignore_low = False


    def process_image(self, data):
        if self.ignore_next:
            self.ignore_next = False
            return
        #do analysis
        publisher = rospy.Publisher('/cmd_vel', Twist, queue_size = 1)
        move = Twist()
        bridge = CvBridge()
        # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # red_ped_looker = frame[height-2*down:height-down,:]
        # cv2.imshow("framerino", red_ped_looker)
        # cv2.waitKey(3)

        frame = bridge.imgmsg_to_cv2(data, desired_encoding="bgr8")
        # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height = frame.shape[0]
        down = 120
        small = frame[height-down:height,:]
        # cv2.imshow("rgb", small)
        # cv2.waitKey(3)

        # Commented out by Thien
        # hsv = cv2.cvtColor(small, cv2.COLOR_BGR2HSV)
        # height, width, depth = hsv.shape
        # cv2.imshow("hsv", hsv)
        # cv2.waitKey(3)

        # time.sleep(60)

        # low_red = np.array([150, 155, 84])
        # high_red = np.array([179, 255, 255])
        # red_mask = cv2.inRange(hsv, low_red, high_red)
        # red = cv2.bitwise_and(hsv, hsv, mask=red_mask)

        # cv2.imshow("red", red)
        # cv2.waitKey(3)

        lek = cv2.cvtColor(small, cv2.COLOR_RGB2GRAY)
        ret, bottom = cv2.threshold(lek,150,255,cv2.THRESH_BINARY)
        
        

        height, width = bottom.shape
        xCount, yCount, num, avX, avY,y_count = 0, 0, 0, 0, 0, 0
        max_width_l, max_width_r, max_height, min_height = 0, width, height, 0
        isYlow = False
        for y in range(0, height):
            max_width_l, max_width_r = 0, width
            for x in range(0, width):
                px = bottom[y, x]
                if px == 255:
                    if x < width/2 and x > max_width_l:
                        max_width_l = x
                    if x > width/2 and x < max_width_r :
                        max_width_r = x
        
            for x in range(max_width_l, max_width_r):
                    if(px == 0):
                        # small[y, x] = [255, 0, 255]
                        num += 1
                        xCount += x
                        yCount += y

        cununt = 0
        for y in range(0, height):
            px = bottom[y, width/2]
            if px == 255:
                cununt += 1
        # print("Cununt: " + str(cununt))
    
        
                
        if num > 0:
            # print("YCOUNT: " + str(y_count))
            avX = int(xCount/num)
            # print(avX, avY)
            avY = int(yCount/num)
            # cv2.circle(small, (avX, avY), 20, (255, 0, 255), -1)
            # cv2.imshow("namew22", small)
            # cv2.waitKey(3)
            # cv2.circle(frame, (avX, avY), 20, (255, 0, 255), -1)
            # cv2.imshow("namew", frame)
            # cv2.waitKey(3)

            base_speed = .2
            base_angular = 0
            KP = .3
            KD = .05
            error = 0
            max_error = 1
            errX = -1 * (avX - width/2.0) / (width/2.0 / max_error)
            # print(str(avY + (480-down)))
            isYLow = (avY + 480-down > 430)
            # if isYLow:
            #     if(errX > 0):
            #         error = max_error
            #     else:
            #         error = -1 * max_error
            # else:
            error = errX


            # print(error)
            if error != 0:
                if isYLow and cununt >= 30 and self.ignore_low is False:

                    print("Start")
                    move.linear.x = 0
                    move.angular.z = 0
                    publisher.publish(move)
                    time.sleep(1)
                    self.turn_degrees(90, publisher, error)
                else:
                    self.ignore_low = False
                    p = KP * error
                    d = KD * abs(error-self.prev_error)
                    g = p + d
                    if base_speed - abs(g) >= 0:
                        move.linear.x = base_speed - abs(g)
                    else:
                        move.linear.x = 0
                    move.angular.z = 3*g
                    publisher.publish(move)
                    self.ignore_next = True

    def turn_degrees(self, degrees, publisher, error):
        move = Twist()
        move.linear.x = 0
        if error > 0:
            move.angular.z = 1
        else:
            move.angular.z = -1
        time_to = degrees / (1 * (180.0/math.pi))
        publisher.publish(move)
        self.ignore_next = True
        self.ignore_low = True
        time.sleep(time_to)
        move.angular.z = 0
        publisher.publish(move)
        print("End")
        time.sleep(1)


        
      






    def doStuff(self):
        rospy.init_node('imIn', anonymous=True)
        rospy.Subscriber('/rrbot/camera1/image_raw', Image, self.process_image, queue_size=1, buff_size=2**24)
        rospy.spin()


    def start(self):
        if __name__ == '__main__':
            time.sleep(5)
            try:
                self.doStuff()
            except rospy.ROSInterruptException:
                pass
        
follower = LineFollower()
follower.start()

