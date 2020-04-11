import anki_vector as av
import cv2 
import numpy as np

def main():
    ANKI_SERIAL = '006046ca'
    ANKI_BEHAVIOR = av.connection.ControlPriorityLevel.OVERRIDE_BEHAVIORS_PRIORITY

    with av.Robot(serial=ANKI_SERIAL, behavior_control_level=ANKI_BEHAVIOR) as robot:
        robot.camera.init_camera_feed()

        while(True):
            # Record camera feed and save it as an avi file
            img = np.array(robot.camera.latest_image.raw_image)

            # SIFT for Block
            detect_image = cv2.imread("plate_label.png", cv2.IMREAD_GRAYSCALE)
            img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            img_blur = cv2.blur(detect_image, (3,3))

            # cv2.imshow("look for", detect_image)

            # Find Features
            sift = cv2.xfeatures2d.SIFT_create()
            kp_image, desc_image = sift.detectAndCompute(img_blur, None)
            kp_grayframe, desc_grayframe = sift.detectAndCompute(img_gray, None)

            # Feature Matching
            index_params = dict(algorithm=0, trees=5)
            search_params = dict()
            flann = cv2.FlannBasedMatcher(index_params, search_params)

            matches = flann.knnMatch(desc_image, desc_grayframe, k = 2)
            
            matchesMask = [[0,0] for i in range(len(matches))]

            for i,(m,n) in enumerate(matches):
                if m.distance < 0.7*n.distance:
                    matchesMask[i] = [1,0]

            draw_params = dict(matchColor = (0,255,0), singlePointColor = (255,0,0), matchesMask = matchesMask, flags = cv2.DrawMatchesFlags_DEFAULT)
            # good_points = []

            # for m,n in matches:
            #     if m.distance < 0.6 * n.distance:
            #         good_points.append(m)
            
            imgtest = cv2.drawMatchesKnn(img_blur, kp_image, img_gray, kp_grayframe, matches, None, **draw_params)
            cv2.imshow('test',imgtest)
            cv2.waitKey(3)
            print(matches)

            # if(len(good_points) > 10):
            #     query_pts = np.float32([kp_image[m.queryIdx].pt for m in good_points]).reshape(-1, 1, 2)
            #     train_pts = np.float32([kp_grayframe[m.trainIdx].pt for m in good_points]).reshape(-1, 1, 2)

            #     matrix, mask = cv2.findHomography(query_pts, train_pts, cv2.RANSAC, 5.0)
            #     matches_mask = mask.ravel().tolist()

            #     # Perspective transform
            #     h, w = detect_image.shape
            #     pts = np.float32([[0, 0], [0, h], [w, h], [w, 0]]).reshape(-1, 1, 2)
            #     dst = cv2.perspectiveTransform(pts, matrix)

            #     # Get bounding box center
            #     # dstXCenter = (dst[0][0][0] + dst[1][0][0] + dst[2][0][0] + dst[3][0][0])/4

            #     homography = cv2.polylines(img_gray, [np.int32(dst)], True, (255, 0, 0), 3)
            #     cv2.imshow("Homography", homography)
            #     cv2.waitKey(3)
            # else:
            #     cv2.imshow("Homography", img_gray)
            #     cv2.waitKey(3)


if __name__ == "__main__":
    main()