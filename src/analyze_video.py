import cv2
import os
import numpy as np
import time

yellow_min = np.array([10,70,75])
yellow_max = np.array([25,150,200])
blue_min = np.array([100,120,0])
blue_max = np.array([120,255,255])
green_min = np.array([80,50,50])
green_max = np.array([90,230,255])
black_min = np.array([0,0,100])
black_max = np.array([100,255,125])
trigger_thresh = 10
noise_thresh = 12
binary_thresh = 40
right_half = 320

def main():
    video_directory = "/home/fizzer/Desktop/ML_Robot_Competition_ENPH353/video/video0.avi"
    directory = "/home/fizzer/Desktop/ML_Robot_Competition_ENPH353/video/"

    os.chdir(directory)
    vidObj = cv2.VideoCapture(video_directory)


    frameCount = 0
    lower_ybound, upper_ybound, upper_xbound, lower_xbound = 0, 0, 0, 0

    while vidObj.isOpened():
        ret, frame = vidObj.read()
        height, width, layer = frame.shape
        right_frame = frame[:, right_half:width]

        if(ret == True):
            
            
            # 640 x 480 pixels
            size = (width, height)
            
            # Convert image to HSV and then produce a blurred binary frame
            hsv = cv2.cvtColor(right_frame, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, blue_min, blue_max)
            res = cv2.bitwise_and(right_frame, right_frame, mask=mask)

            greyFrame = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
            ret, binaryFrame = cv2.threshold(greyFrame, 0, 255, cv2.THRESH_BINARY)
            blurFrame = cv2.blur(binaryFrame, (5,5))

            frameArray = np.asarray(blurFrame)

            horiArray = np.zeros(height)
            vertArray = np.zeros((width))

            # Only analyze after a certain number of frames
            if (frameCount < 0):
                frameCount += 1
            else:
                # Cut frame to only the right half
                for x in range(width - right_half):
                    for y in range(height):
                        # Determine important areas from vertical slices along the horizontal
                        if(frameArray[y][x] > binary_thresh):
                            horiArray[x] += 1

                # Filters values below a threshhold to remove noise
                horiArray = [0 if horiArray_ < noise_thresh else int(horiArray_) for horiArray_ in horiArray]

                # print("Hori Array")
                # print(horiArray)
                flagFirst = False
                # lastVal = 0
                
                # Horizontal Bounds
                for i in range(len(horiArray)):
                    if (flagFirst == False and horiArray[i] > trigger_thresh):
                        # print("Hori lower", i)
                        lower_xbound = i
                        flagFirst = True
                    if (flagFirst == True and horiArray[i] < trigger_thresh):
                        # print("Hori upper", i)
                        upper_xbound = i
                        flagFirst = False
                        lastVal = 0
                        break
                    # lastVal = horiArray[i]
                    
                # Determine important areas from horizontal slices along y
                for y in range(height):
                    for x in range(lower_xbound, upper_xbound):
                        if(frameArray[y][x] > binary_thresh):
                            vertArray[y] += 1

                vertArray = [0 if vertArray_ < noise_thresh else int(vertArray_) for vertArray_ in vertArray]
                
                # print("Vert Array")
                # print(vertArray)

                # Vertical Bounds
                for i in range(len(vertArray)):
                    if (flagFirst == False and vertArray[i] > trigger_thresh):
                        # print("Hori lower", i)
                        lower_ybound = i
                        flagFirst = True
                    if (flagFirst == True and vertArray[i] < trigger_thresh):
                        # print("Hori upper", i)
                        upper_ybound = i
                        flagFirst = False
                        lastVal = 0
                        break



                frameCount = 0

            # Draw a bounding box and circle for the center of mass
            if ((upper_xbound - lower_xbound > 0) and (upper_ybound - lower_ybound > 0)):
                cv2.rectangle(res, (lower_xbound, lower_ybound), (upper_xbound, upper_ybound), (0,255,0), 1)
                car_frame = right_frame[lower_ybound:upper_ybound, lower_xbound:upper_xbound]
                cv2.imshow("Car", car_frame)

                plateFrame = cv2.cvtColor(car_frame, cv2.COLOR_BGR2HSV)
                blackMask = cv2.inRange(plateFrame, black_min, black_max) 
                result = cv2.bitwise_and(car_frame, car_frame, mask = blackMask) 
                # cv2.imshow("plate", plateFrame)
                cv2.imshow("result", result)

            print(lower_ybound)
            print(upper_ybound)
            print(lower_xbound)
            print(upper_xbound)
            
            

            cv2.imshow("Raw", right_frame)
            cv2.imshow("Res", res)
            
            cv2.waitKey(3)
            
            # time.sleep(1)

        # out = cv2.VideoWriter('analyze.avi', cv2.VideoWriter_fourcc(*'DIVX'), 120, size)

        # for i in range(len(out_array)):
        #     out.write(out_array[i])
        # out.release

if __name__ == "__main__":
    main()