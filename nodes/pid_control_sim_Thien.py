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
        self.state = 0
        self.elestart = 0


    def process_image(self, data):
        # print("\n State: {}".format(self.state))
        #set up publisher
        publisher = rospy.Publisher('/cmd_vel', Twist, queue_size = 1)
        move = Twist()
        bridge = CvBridge()

        #ignore the image in the queue if have just turned - will be from old position
        if self.ignore_next:
            self.ignore_next = False
            return
        
        if self.state == 13:
            # print("YAY")
            move.linear.x = 0
            move.angular.z = 1
            publisher.publish(move)
            return
        #convert ROS image to openCV image, bgr format, use bottom 120 pixels for PID
        frame = bridge.imgmsg_to_cv2(data, desired_encoding="bgr8")
        height, width, __ = frame.shape

        if self.state in [6,10]:
            #cross crosswalk
            ped_im = frame[height-160:height-100,:]
            if self.safe_to_go(ped_im):
                print("FULL STEAM AHEAD")
            else:
                move.linear.x = 0
                move.angular.z = 0
                publisher.publish(move)
                # print("Man in Crosswalk")
                return
        
            


        down = 100
        small = frame[height-down:height,:]

        #show FOV of PID
        # cv2.imshow("bgr", small)
        # cv2.waitKey(3)

        #check for crosswalk
        start_walk, see_walk = self.is_crosswalk(small)
        if start_walk:
            if self.state in [6,10]:
                pass
            elif self.state == 1:
                # print("----CROSSWALK----")
                move.linear.x = 0
                move.angular.z = 0
                publisher.publish(move)
                time.sleep(0.5)
                self.turn_degrees(125, publisher, "r")
                self.state += 1
                self.ignore_next = True
                time.sleep(0.5)
            elif self.state in [5,9]:
                # print("----CROSSWALK----")
                move.linear.x = 0
                move.angular.z = 0
                publisher.publish(move)
                time.sleep(0.1)
                # print("Need to Cross Crosswalk")
                self.state += 1
                self.ignore_next = True
                time.sleep(0.1)
                return
        if self.state in [6,10] and not see_walk:
            self.state += 1
            cv2.destroyAllWindows()
            return

        #binary threshold image for PID processing
        lek = cv2.cvtColor(small, cv2.COLOR_RGB2GRAY)
        ret, bottom = cv2.threshold(lek,200,255,cv2.THRESH_BINARY)
        
        

        height, width = bottom.shape
        xCount, yCount, num, avX, avY = 0, 0, 0, 0, 0
        max_width_l, max_width_r = 0, width
        isYlow = False

        #define the edges of the track, for finding the center of mass, then count all interior black points
        for y in range(0, height):
            max_width_l, max_width_r = 0, width
            if self.state not in [6, 10]:
                for x in range(0, width):
                    px = bottom[y, x]
                    if px == 255:
                        if x < width/2 and x > max_width_l:
                            max_width_l = x
                        if x > width/2 and x < max_width_r :
                            max_width_r = x
        
            for x in range(max_width_l, max_width_r):
                    px = bottom[y,x]
                    if(px == 0):
                        # small[y, x] = [255, 0, 255]
                        num += 1
                        xCount += x
                        yCount += y

        #"cununt" is the number of white pixels directly in front of our robot - used to know when to turn
        cununt = 0
        for y in range(0, height):
            px = bottom[y, width/2]
            if px == 255:
                cununt += 1
        # print("Cununt: " + str(cununt))
    
        
        #if any black pixels in area to search do PID otherwise keep doing what doing
        if num > 0:
            avX = int(xCount/num)
            avY = int(yCount/num)

            #----START PID----
            #Tuned constants, check if Y_avg is low (a sign we need to turn)
            base_speed = .2
            base_angular = 0
            KP = .22
            KD = .05
            error = 0
            max_error = 1
            errX = -1 * (avX - width/2.0) / (width/2.0 / max_error)
            isYLow = (avY + 480-down > 425)
            error = errX


            if error != 0:
                #checks if Y_avg is low and lots of white pixels dead ahead, means we are at a corner and should turn
                if (isYLow and cununt >= 30 and self.ignore_low is False and self.state not in [6,10]):
                    time.sleep(0.1)
                    # print("Start Turn")
                    move.linear.x = 0
                    move.angular.z = 0
                    publisher.publish(move)
                    time.sleep(1)
                    if self.state in [0,3]:
                        self.turn_degrees(115, publisher, "r")
                    elif self.state == 7:
                        self.turn_degrees(110, publisher, "r")
                    elif self.state == 8:
                        self.turn_degrees(115, publisher, "r")    
                    else:
                        self.turn_degrees(110, publisher, "r")
                    self.state += 1
                else:
                    #do PID and publish new value
                    self.ignore_low = False
                    p = KP * error
                    d = KD * abs(error-self.prev_error)
                    g = p + d
                    if base_speed - abs(g) >= 0:
                        move.linear.x = base_speed - abs(g)
                    else:
                        move.linear.x = 0
                    move.angular.z = 2.7*g
                    publisher.publish(move)
            if(self.state == 11):
                if self.elestart == 0:
                    self.elestart = time.time()
                # print(time.time() - self.elestart)
                if self.elestart != 0 and time.time() - self.elestart > 6.5:
                    self.turn_degrees(85, publisher, "r")
                    self.state += 1
        

    def turn_degrees(self, degrees, publisher, direction):
        move = Twist()
        move.linear.x = 0

        #decide which way to turn
        if direction == "r":
            move.angular.z = -1
        else:
            move.angular.z = 1

        #time needed to turn given degrees at 1 rad/s
        time_to = degrees / (1 * (180.0/math.pi))
        publisher.publish(move)
        self.ignore_next = True
        self.ignore_low = True
        time.sleep(time_to)
        move.angular.z = 0
        publisher.publish(move)
        # print("End Turn")
        time.sleep(1)

    def is_crosswalk(self, image):
        #use bottom 50 pixels
        height = image.shape[0]
        hsv = image[height-50:height,:]
        hsv = cv2.cvtColor(hsv, cv2.COLOR_BGR2HSV)

        # lower mask (0-10)
        lower_red = np.array([0,50,50])
        upper_red = np.array([10,255,255])
        mask0 = cv2.inRange(hsv, lower_red, upper_red)

        # upper mask (170-180)
        lower_red = np.array([170,50,50])
        upper_red = np.array([180,255,255])
        mask1 = cv2.inRange(hsv, lower_red, upper_red)

        mask = mask0 + mask1
        mask_sum = np.sum(mask)
        # print("red mask: " + str(mask_sum))
        #threshold for action - close enough to crosswalk
        start_sum = False
        see_sum = False
        if mask_sum > 1000000:
            start_sum = True
        if mask_sum > 1:
            see_sum = True
        
        return (start_sum, see_sum)

    def safe_to_go(self, image):
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        #mask
        lower_blue = np.array([100,150,0])
        upper_blue = np.array([140,255,255])
        mask = cv2.inRange(hsv, lower_blue, upper_blue)
        mask = mask[:,0:420]
        # cv2.imshow("blue mask walk", mask)
        # cv2.waitKey(3)

        mask_sum = np.sum(mask)

        # print("blue mask: {}".format(mask_sum))
        if mask_sum < 200:
            return True
        return False

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

