import anki_vector as av
from anki_vector.util import degrees
import cv2 
import numpy as np

def main():
    ANKI_SERIAL = '006046ca'
    ANKI_BEHAVIOR = av.connection.ControlPriorityLevel.OVERRIDE_BEHAVIORS_PRIORITY
    #Hue values
    GREEN = 60
    YELLOW = 30
    BLUE = 120
    MIN_SAT = 100
    MIN_VAL = 100
    MAX_SAT = 255
    MAX_VAL = 255

    with av.Robot(serial=ANKI_SERIAL, behavior_control_level=ANKI_BEHAVIOR) as robot:
        robot.camera.init_camera_feed()
        robot.behavior.set_head_angle(degrees(5.0))

        while(True):
            # Record camera feed and save it as an avi file
            raw_img = np.array(robot.camera.latest_image.raw_image)
            img = cv2.cvtColor(raw_img, cv2.COLOR_RGB2BGR)

            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

            lower_bound = np.array([70,MIN_SAT,MIN_VAL])
            upper_bound = np.array([130,MAX_SAT,MAX_VAL])

            green_mask = cv2.inRange(hsv, np.array([GREEN-10,MIN_SAT,MIN_VAL-50]), np.array([GREEN+10,MAX_SAT,MAX_VAL-50]))
            blue_mask = cv2.inRange(hsv, np.array([BLUE-10,MIN_SAT,MIN_VAL]), np.array([BLUE+10,MAX_SAT,MAX_VAL]))
            yellow_mask = cv2.inRange(hsv, np.array([YELLOW-10,MIN_SAT,MIN_VAL]), np.array([YELLOW+10,MAX_SAT,MAX_VAL]))

            # res = cv2.bitwise_and(img, img, mask=mask)

            cv2.imshow("capture", img)
            cv2.waitKey(3)
            cv2.imshow("green mask", green_mask)
            cv2.waitKey(3)
            cv2.imshow("blue mask", blue_mask)
            cv2.waitKey(3)
            cv2.imshow("yellow mask", yellow_mask)
            cv2.waitKey(3)
            # cv2.imshow("res", res)
            # cv2.waitKey(3)



if __name__ == "__main__":
    main()