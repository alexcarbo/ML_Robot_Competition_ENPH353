import anki_vector as av
import cv2
import numpy as np
from anki_vector.util import degrees
from anki_vector.util import Distance
import time


class PID:

    def __init__(self):
        self.prev_error = 0
        self.count = 0
        self.angle = -80


    def main(self):
        
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
                bottom = frame[height-100:height, 100:width-100]
                bottom = cv2.cvtColor(bottom, cv2.COLOR_BGR2GRAY)
                ret, bottom = cv2.threshold(bottom,80,255,cv2.THRESH_BINARY)
                # cv2.imshow("name", bottom)
                # cv2.waitKey(3)
                    

                height, width = bottom.shape
                xCount, yCount, num, avX, avY,y_count = 0, 0, 0, 0, 0, 0
                max_width_l, max_width_r = 0, width
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
                    # print("MAX WIDTH LEFT: " + str(max_width_l))
                    # print("MAX WIDTH RIGHT: " + str(max_width_r))
                    for x in range(max_width_l, max_width_r):
                        if(px == 0):
                            num += 1
                            xCount += x
                            yCount += y
                
                if num > 0:
                    print("YCOUNT: " + str(y_count))
                    avX = int(xCount/num)
                    print(avX, avY)
                    avY = int(yCount/num)
                    cv2.circle(bottom, (avX, avY), 20, (255, 0, 255), -1)
                    cv2.imshow("namew", bottom)
                    cv2.waitKey(3)

                    base_speed = 60
                    KP = 1.5
                    KD = .3
                    error = 0
                    max_error = 2.5
                    errX = -1 * (avX - width/2.0) / (width/2.0 / max_error)
                    proximity = robot.proximity.last_sensor_reading
                    if(proximity is not None):
                        print("dist: "+ str(proximity.distance.distance_mm))
                        if(proximity.distance.distance_mm < 75.00):
                            robot.motors.stop_all_motors()
                            robot.behavior.say_text("ICEBERG, DEAD AHEAD")
                            robot.behavior.turn_in_place(degrees(self.angle))
                            self.count+=1
                        elif(proximity.distance.distance_mm < 300 and proximity.distance.distance_mm > 280 and (self.count - 1) % 8 == 0):
                            robot.motors.stop_all_motors()
                            robot.behavior.say_text("MIDDLE TURN")
                            time.sleep(1)
                            robot.behavior.say_text("MOM GET THE CAMERA")
                            time.sleep(1)
                            robot.behavior.turn_in_place(degrees(self.angle - 10))
                            self.count+=1
                    error = errX
                    print("Error: " + str(error))
                    if(error != 0):
                        p = KP * error
                        d = KD * 1 * abs(error - self.prev_error)
                        g = p + d
                        print("G: " + str(g)) 
                    else:
                        g = 0
                    print("left: " + str(base_speed-10*g) + "right: " + str(base_speed - 10*g))
                    robot.motors.set_wheel_motors(base_speed - g*10, base_speed + g*10)
                    self.prev_error = error


            

if __name__ == "__main__":
    controlPID = PID()
    controlPID.main()