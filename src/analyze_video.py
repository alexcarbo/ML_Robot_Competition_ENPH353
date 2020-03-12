import cv2
import os
import numpy as np
import time

def main():
    video_directory = "/home/fizzer/Desktop/ML_Robot_Competition_ENPH353/src/data/green_car.avi"
    directory = "/home/fizzer/Desktop/ML_Robot_Competition_ENPH353/src/data/"

    os.chdir(directory)
    vidObj = cv2.VideoCapture(video_directory)
    yellow_min = np.array([15,70,180])
    yellow_max = np.array([35,255,255])
    blue_min = np.array([100,50,50])
    blue_max = np.array([120,200,200])
    green_min = np.array([80,50,50])
    green_max = np.array([90,230,255])

    xsum, ysum, xcount, ycount, frameCount, xCenter, yCenter = 0,0,0,0,0,0,0
    lower_ybound, upper_ybound, upper_xbound, lower_xbound = 0, 0, 0, 0

    while vidObj.isOpened():
        ret, frame = vidObj.read()
        out_array = []

        if(ret == True):
            height, width, layer = frame.shape
            size = (width, height)

            # Convert image to HSV and then produce a blurred binary frame
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            mask = cv2.inRange(hsv, green_min, green_max)
            res = cv2.bitwise_and(frame, frame, mask=mask)

            greyFrame = cv2.cvtColor(res, cv2.COLOR_BGR2GRAY)
            ret, binaryFrame = cv2.threshold(greyFrame, 30, 255, cv2.THRESH_BINARY)
            blurFrame = cv2.blur(binaryFrame, (3,3))

            frameArray = np.asarray(blurFrame)
            size = frameArray.shape
            print(size)

            vertArray = np.zeros(height)
            horiArray = np.zeros((width))

            if (frameCount < 120):
                frameCount += 1
            else:
                xsum, ysum, xcount, ycount = 0,0,0,0
                for y in range(height):
                    for x in range(width):
                        if(frameArray[y][x] > 40):
                            xsum += x
                            ysum += y
                            horiArray[x] += 1
                            vertArray[y] += 1

                xcount = int(np.sum(horiArray))
                ycount = int(np.sum(vertArray))
                xCenter = int(xsum/xcount)
                yCenter = int(ysum/ycount)
                frameCount = 0

                print(horiArray)
                flagFirst = False
                lastVal = 0
                # Vertical Bounds
                for i in range(len(vertArray)):
                    if (flagFirst == False and vertArray[i] > 20):
                        print("lower", i)
                        lower_ybound = i
                        flagFirst = True
                    if (flagFirst == True and lastVal > vertArray[i] and vertArray[i] < 20):
                        print("upper", i)
                        upper_ybound = i
                        flagFirst = False
                        lastVal = 0
                        break
                    lastVal = vertArray[i]

                # Horizontal Bounds
                for i in range(len(horiArray)):
                    if (flagFirst == False and horiArray[i] > 20):
                        print("lower", i)
                        lower_xbound = i
                        flagFirst = True
                    if (flagFirst == True and lastVal > horiArray[i] and horiArray[i] < 20):
                        print("upper", i)
                        upper_xbound = i
                        flagFirst = False
                        lastVal = 0
                        break
                    lastVal = horiArray[i]



            cv2.rectangle(res, (lower_xbound, lower_ybound), (upper_xbound, upper_ybound), (0,255,0), 1)
            cv2.circle(res, (xCenter,yCenter), 5, (0,255,0), 5)

            cv2.imshow("Raw", frame)
            cv2.imshow("Res", res)
            cv2.imshow("blue", blurFrame)
            cv2.waitKey(3)

        out = cv2.VideoWriter('analyze.avi', cv2.VideoWriter_fourcc(*'DIVX'), 120, size)

        for i in range(len(out_array)):
            out.write(out_array[i])
        out.release

if __name__ == "__main__":
    main()