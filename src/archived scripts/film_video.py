import anki_vector as av
from anki_vector.util import degrees
import cv2
import numpy as np
import os



def main():
    ANKI_SERIAL = '006046ca'
    ANKI_BEHAVIOR = av.connection.ControlPriorityLevel.OVERRIDE_BEHAVIORS_PRIORITY

    directory = "/home/fizzer/Desktop/ML_Robot_Competition_ENPH353/video/"

    os.chdir(directory)

    x = 0

    with av.Robot(serial=ANKI_SERIAL, behavior_control_level=ANKI_BEHAVIOR) as robot:
        robot.camera.init_camera_feed()
        robot.behavior.set_head_angle(degrees(5.0))
        robot.behavior.set_lift_height(1.0)
        count = 0
        img_array = []

        robot.motors.set_wheel_motors(40,40)
        while(True):
            # proximity_data = robot.proximity.last_sensor_reading
            # print(proximity_data.distance.distance_mm)
            # Record camera feed and save it as an avi file
            raw_img = np.array(robot.camera.latest_image.raw_image)
            img = cv2.cvtColor(raw_img, cv2.COLOR_RGB2BGR)
            height, width, layers = img.shape
            size = (width, height)
            img_array.append(img)

            cv2.imshow('Anki Camera', img)
            cv2.waitKey(3)

            if (count == 1200):
                break

            count += 1

        out = cv2.VideoWriter('test{}.avi'.format(x), cv2.VideoWriter_fourcc(*'DIVX'), 120, size)
        
        for i in range(len(img_array)):
            out.write(img_array[i])
        out.release

if __name__ == "__main__":
    main()