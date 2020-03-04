import anki_vector as av
from anki_vector.util import degrees
import cv2
import numpy as np

def main():
    ANKI_SERIAL = '006046ca'
    ANKI_BEHAVIOR = av.connection.ControlPriorityLevel.OVERRIDE_BEHAVIORS_PRIORITY

    with av.Robot(serial=ANKI_SERIAL,
        behavior_control_level=ANKI_BEHAVIOR) as robot:
        robot.camera.init_camera_feed()

        while(True):
            proximity_data = robot.proximity.last_sensor_reading
            distance = proximity_data.distance.distance_mm
            
            if proximity_data is not None:
                # print('Proximity distance: {0}'.format(proximity_data.distance))
                print("Distance in mm: ", proximity_data.distance.distance_mm)

            block_img = cv2.imread("IMG_1583.jpg", cv2.IMREAD_GRAYSCALE)
            img = robot.camera.latest_image.raw_image
            img_gray = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2GRAY)

            # vid_h, vid_w = img_gray.shape

            cv2.imshow('Anki Camera', img_gray)
            cv2.waitKey(3)

            # #Features
            # sift = cv2.xfeatures2d.SIFT_create()
            # kp_image, desc_image = sift.detectAndCompute(block_img, None)

            # #Feature matching
            # index_params = dict(algorithm=0, trees=5)
            # search_params = dict()
            # flann = cv2.FlannBasedMatcher(index_params, search_params)
            


            # kp_grayframe, desc_grayframe = sift.detectAndCompute(img_gray, None)
            # matches = flann.knnMatch(desc_image, desc_grayframe, k = 2)
            # good_points = []

            # for m, n in matches:
            #     if m.distance < 0.6 * n.distance:
            #         good_points.append(m)

            # if(len(good_points) > 5):
            #     query_pts = np.float32([kp_image[m.queryIdx].pt for m in good_points]).reshape(-1, 1, 2)
            #     train_pts = np.float32([kp_grayframe[m.trainIdx].pt for m in good_points]).reshape(-1, 1, 2)

            #     matrix, mask = cv2.findHomography(query_pts, train_pts, cv2.RANSAC, 5.0)
            #     matches_mask = mask.ravel().tolist()

            #     # Perspective transform
            #     h, w = block_img.shape
            #     pts = np.float32([[0, 0], [0, h], [w, h], [w, 0]]).reshape(-1, 1, 2)
            #     dst = cv2.perspectiveTransform(pts, matrix)

            #     # Get bounding box center
            #     dstXCenter = (dst[0][0][0] + dst[1][0][0] + dst[2][0][0] + dst[3][0][0])/4

            #     homography = cv2.polylines(img_gray, [np.int32(dst)], True, (255, 0, 0), 3)
            #     cv2.imshow("Homography", homography)
            #     cv2.waitKey(3)

            #     # Stay close to block
            #     if(dstXCenter - vid_w/2 > 100):
            #         robot.motors.set_wheel_motors(20,-20)
            #     elif(dstXCenter - vid_w/2 < -50):
            #         robot.motors.set_wheel_motors(-20,20)
            #     else:
            #         if(distance > 100):
            #             robot.motors.set_wheel_motors(20,20)
            #         else:
            #             robot.motors.set_wheel_motors(0,0)

            # else:
            #     cv2.imshow("Homography", img_gray)
            #     cv2.waitKey(3)

            #     robot.motors.set_wheel_motors(20,-20)
            


if __name__ == "__main__":
    main()