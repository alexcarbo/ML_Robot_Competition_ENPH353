#!/usr/bin/env python
import sys
import os
import roslib
import cv2
import numpy as np
import time
import math
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError
from geometry_msgs.msg import Twist
import rospy
import constants as const
import savePlateCount
roslib.load_manifest('competition_2019t2')

class DetectPlate:
    '''Detects License Plates'''

    def __init__(self):
        # Setup bridging between image message and OpenCV
        self.bridge = CvBridge()
        self.move = Twist()
        self.save_plate_count = savePlateCount.savePlateCount()

        # Setup publisher and subscribers
        self.image_pub = rospy.Publisher('image_topic_2', Image)
        self.image_sub = rospy.Subscriber("/rrbot/camera1/image_raw", Image, self.callBack)
        self.vel_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=1)

        # Setup save directory for plates
        self.directory = "/home/fizzer/Desktop/353_ws/plates/"
        os.chdir(self.directory)
        self.plate_count = 0

        self.captured_flag = False

        # Controls drawing identified corners and contours
        self.debug = False

    def callBack(self, data):
        try:
            # Convert Image message to OpenCV
            image_feed = self.bridge.imgmsg_to_cv2(data, "bgr8")
        except CvBridgeError as exception:
            print(exception)

        cv2.imshow("Image Feed", image_feed)
        cv2.waitKey(const.IMSHOW_WAIT)

        # Convert image to HSV and then produce a blurred binary frame
        hsv = cv2.cvtColor(image_feed, cv2.COLOR_BGR2HSV)

        # blue_mask = cv2.inRange(hsv, const.BLUE_MIN, const.BLUE_MAX)
        # green_mask = cv2.inRange(hsv, const.GREEN_MIN, const.GREEN_MAX)
        # yellow_mask = cv2.inRange(hsv, const.YELLOW_MIN, const.YELLOW_MAX)
        black_mask = cv2.inRange(hsv, const.BLACK_MIN, const.BLACK_MAX)
        blur_plate_frame = cv2.blur(black_mask, (3, 3))
        
        # blue_res = cv2.bitwise_and(right_frame, right_frame, mask=blue_mask)
        # green_res = cv2.bitwise_and(right_frame, right_frame, mask=green_mask)
        # yellow_res = cv2.bitwise_and(right_frame, right_frame, mask=yellow_mask)
        # black_res = cv2.bitwise_xor(right_frame, right_frame, mask=black_mask)
        
        # Contains the index for the plate contour in contour and it's y-center
        plate_contours_index = []
        # Contrains the plate contours
        plate_contours = []
        
        # Find the contours from the black mask
        _, contours, hierarchy = cv2.findContours(blur_plate_frame, cv2.RETR_TREE,
                                                  cv2.CHAIN_APPROX_SIMPLE)
        contour_img = np.zeros((blur_plate_frame.shape[0], blur_plate_frame.shape[1], 3),
                               dtype=np.uint8)
        for i, e in enumerate(contours):
            # Filter out all smaller contours
            if cv2.contourArea(contours[i]) > const.CONTOUR_AREA_MIN:
                # print("Contour Area: ", cv2.contourArea(contours[i]))
                y_center = 0
                for j, f in enumerate(contours[i]):
                    y_center += contours[i][j][0][1]
                y_center /= len(contours[i])
                # If the array is empty add the first entry
                if plate_contours_index == []:
                    plate_contours_index.append([i, y_center])
                    plate_contours.append(contours[i])
                else:
                    # Check for contours that aren't closeby in height to contours in array already
                    for k, g in enumerate(plate_contours_index):
                        # Limit to two contours for two plates
                        if (abs(y_center - plate_contours_index[k][1]) > const.CONTOUR_MIN_Y_DIST and
                                len(plate_contours_index) < const.MAX_CONTOURS):
                            plate_contours_index.append([i, y_center])
                            plate_contours.append(contours[i])

        # Look for contour corners if they meet our size criterion
        if len(plate_contours) == const.MAX_CONTOURS:
            if not self.captured_flag:
                for i, e in enumerate(plate_contours):
                    cv2.drawContours(contour_img, plate_contours, i, const.LINE_COLOUR,
                                     const.LINE_THICKNESS, cv2.LINE_8, hierarchy, 0)
                if self.debug:
                    cv2.imshow("contours", contour_img)
                    cv2.waitKey(const.IMSHOW_WAIT)

                # Get the corners of the contours
                grey_contour = cv2.cvtColor(contour_img, cv2.COLOR_BGR2GRAY)
                gray = np.float32(grey_contour)
                dst = cv2.cornerHarris(gray, 10, 3, 0.04)

                dst = cv2.dilate(dst, None)
                _, dst = cv2.threshold(dst, 0.1*dst.max(), 255, 0)  # _ Refers to ret
                dst = np.uint8(dst)
                _, _, _, centroids = cv2.connectedComponentsWithStats(dst)  # _ Refer to ret, label and stats
                criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.001)
                corners = cv2.cornerSubPix(gray, np.float32(centroids), (5, 5), (-1, -1), criteria)
                
                # print("Number of corners: ", len(corners))
                if self.debug:
                    for i in range(1, len(corners)):
                        cv2.circle(contour_img, (int(corners[i, 0]), int(corners[i, 1])),
                                   const.CIRCLE_RADIUS, const.LINE_COLOUR, const.CIRCLE_THICKNESS)
                    contour_img[dst>0.1*dst.max()] = [0, 0, 255]

                # Corner points of each plate
                parking_plate = []
                license_plate = []
                plate_dims = (const.PLATE_WIDTH, const.PLATE_HEIGHT)

                # Checks for 8 corners plus one at the center by definition
                if len(corners) == const.CORNERS_NEEDED:
                    # Corners given from top of frame to bottom, so corners 1-4 are the top plate
                    # corners 5-9 are the bottom plate. Corner 1 is at the center and is diregarded
                    for i in range(1, 5):
                        parking_plate.append(list(corners[i]))
                    for i in range(5, 9):
                        license_plate.append(list(corners[i]))

                    parking_plate = np.float32(parking_plate)
                    license_plate = np.float32(license_plate)
                    plate_size = np.float32([[0,0], [plate_dims[0],0], [0,plate_dims[1]],
                                             [plate_dims[0], plate_dims[1]]])

                    # Get the transformation matrix for the plates to be rectangular and flat
                    parking_matrix = cv2.getPerspectiveTransform(parking_plate, plate_size)
                    parking_plate = cv2.warpPerspective(image_feed, parking_matrix, plate_dims)

                    license_matrix = cv2.getPerspectiveTransform(license_plate, plate_size)
                    license_plate = cv2.warpPerspective(image_feed, license_matrix, plate_dims)

                    # Record the number of plates saved in a pickle file
                    try:
                        self.save_plate_count.load_plates("plate_count")
                        self.plate_count = self.save_plate_count.get_plate_count()
                    except (OSError, IOError) as e:
                        self.save_plate_count.save_plates("plate_count")
                        self.plate_count = self.save_plate_count.get_plate_count()

                    # Save the plates
                    cv2.imwrite("parking{}.jpg".format(self.plate_count), parking_plate)
                    cv2.imwrite("license{}.jpg".format(self.plate_count), license_plate)
                    
                    # Update count on the number of plates saved
                    self.plate_count += 1
                    self.save_plate_count.update_plate_count(self.plate_count)
                    self.save_plate_count.save_plates("plate_count")

                    cv2.imshow("Parking Plate", parking_plate)
                    cv2.imshow("License Plate", license_plate)
                    cv2.waitKey(const.IMSHOW_WAIT)
                    self.captured_flag = True
        else:
            self.captured_flag = False

def main(args):
    rospy.init_node('DetectPlate', anonymous=True)
    detect_plate = DetectPlate()
    rospy.spin()

if __name__ == '__main__':
    main(sys.argv)
    cv2.destroyAllWindows
    