import anki_vector as av
import cv2
import numpy as np
from anki_vector.util import degrees
from anki_vector.util import Distance
import time


ANKI_SERIAL = '006046ca'
ANKI_BEHAVIOR = av.connection.ControlPriorityLevel.OVERRIDE_BEHAVIORS_PRIORITY
    

with av.Robot(serial=ANKI_SERIAL,
            behavior_control_level=ANKI_BEHAVIOR) as robot:

    #MOST IMPORTANT PART: make eyes green, get parts in position where it can see block
    robot.behavior.set_eye_color(.21,1.00)
    robot.behavior.set_head_angle(degrees(5.0))
    robot.behavior.set_lift_height(1.0)
    robot.camera.init_camera_feed()
            
    while True:
         #get image from robot
        img_pil = robot.camera.latest_image.raw_image
        frame = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
        height, width, depth = frame.shape
        cv2.imshow("name1", frame)  
        cv2.waitKey(3)   

        bottom = frame[height-200:height-100, 100:width-100]   
        cv2.imshow("name", bottom)  
        cv2.waitKey(3)         
        height, width, depth = bottom.shape
        pink_count = 0

        # for y in range(0, height):
        #     for x in range(0, width):
        #         px = bottom[y, x]

                
              