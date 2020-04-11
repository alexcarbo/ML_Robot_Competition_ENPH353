#!/usr/bin/env python
from __future__ import print_function

import roslib
roslib.load_manifest('competition_2019t2')
import sys
import cv2
import numpy as np
import os
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
from geometry_msgs.msg import Twist
import rospy
from std_msgs.msg import String

class capture_video:
    FRAMES_PER_VIDEO = 1200

    def __init__(self):
        # SETTINGS TO ADJUST TO RECORD VIDEO
        self.record_flag = False
        self.video_name = "Test"

        # Setup bridging between image message and OpenCV
        self.bridge = CvBridge()
        self.move = Twist()

        # Setup publisher and subscribers
        self.image_pub = rospy.Publisher('image_topic_2', Image)
        self.image_sub = rospy.Subscriber("/rrbot/camera1/image_raw", Image, self.callBack)  
        self.vel_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=1)

        # Setup saving directory for recording video
        self.directory = "/home/fizzer/Desktop/ML_Robot_Competition_ENPH353/video/"
        os.chdir(self.directory)

        # Setup variables to stored frames for a video
        self.frame_count = 0
        self.img_array = []
        self.video_count = 0



    def callBack(self, data):
        try:
            # Convert Image message to OpenCV
            cv_image = self.bridge.imgmsg_to_cv2(data, "bgr8")
        except CvBridgeError as e:
            print(e)

        

        if self.record_flag == True:
            cv2.imshow("Robot video feed", cv_image)
            cv2.waitKey(3)

            # Give the shape of the image
            (height,width,channels) = cv_image.shape
            size = (width, height)
            self.img_array.append(cv_image)

            # Save video after a set number of frames
            if (self.frame_count == self.FRAMES_PER_VIDEO):
                out = cv2.VideoWriter('{}{}.avi'.format(self.video_name, self.video_count), cv2.VideoWriter_fourcc(*'DIVX'), 30, size)
                
                for i in range(len(self.img_array)):
                    out.write(self.img_array[i])
                out.release

                self.frame_count = 0
                self.video_count += 1
                self.img_array = []
                print("Saviing Video")
            else:
                self.frame_count += 1
        
def main(args):
    rospy.init_node('capture_video', anonymous=True)
    ic = capture_video()
    

    rospy.spin()

# Setup up main loop
if __name__ == '__main__':
    main(sys.argv)
    cv2.destroyAllWindows()