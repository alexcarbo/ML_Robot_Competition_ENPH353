import cv2
import os
import numpy as np

# This script is to test out object detection algorithms without needing to run Gazebo

# HSV values organized by [Hue, Saturation, Value]. Hue is the colour shade, saturation is of strong
# that colour is, and value is how bright it is
YELLOW_MIN = np.array([10,50,0])
YELLOW_MAX = np.array([40,2550,255])
BLUE_MIN = np.array([100,120,0])
BLUE_MAX = np.array([120,255,255])
GREEN_MIN = np.array([50,50,0])
GREEN_MAX = np.array([70,255,255])
BLACK_MIN = np.array([0,0,0])
BLACK_MAX = np.array([255,255,20])

IMSHOW_WAIT = 3

# These thresholds filter out the alphanumerics in the license plates to obtain the boundaries
ROW_THRESH = 60
COLUMN_THRESH = 60
BOUNDARY_THRESH = 10
PLATE_Y_OFFSET = 10
X_MIN_SIZE = 65
PLATE_MIN_SIZE = 30
LINE_COLOUR = (105,255,180)
LINE_THICKNESS = 1

BINARY_THRESH = 40
WIDTH_CROP_MIN = 0.75 # Take the this percentage of the width to the full width length
WIDTH_CROP_MAX = 1
HEIGHT_CROP_MIN = 0.4
HEIGHT_CROP_MAX = 0.85

def main():
    # Setup directories to find videos
    video_directory = "/home/fizzer/Desktop/ML_Robot_Competition_ENPH353/video/BlueCar0.avi"
    directory = "/home/fizzer/Desktop/ML_Robot_Competition_ENPH353/video/"

    os.chdir(directory)
    vidObj = cv2.VideoCapture(video_directory)

    frame_count = 0

    # Load video
    while vidObj.isOpened():
        ret, frame = vidObj.read()
        height, width, layer = frame.shape
        # 640 x 480 pixels
        size = (width, height)

        width_min = int(WIDTH_CROP_MIN * width)
        width_max = int(WIDTH_CROP_MAX * width)
        height_min = int(HEIGHT_CROP_MIN * height)
        height_max = int(HEIGHT_CROP_MAX * height)
        crop_width = width_max - width_min
        crop_height = height_max - height_min
        
        right_frame = frame[height_min:height_max, width_min:width_max]

        # cv2.imshow("Cropped Frame", right_frame)
        # cv2.waitKey(IMSHOW_WAIT)

        if(ret == True):
            parking_plate_y = [0,0]
            license_plate_y = [0,0]
            x_bound = [0,0]

            # Convert image to HSV and then produce a blurred binary frame
            hsv = cv2.cvtColor(right_frame, cv2.COLOR_BGR2HSV)

            blue_mask = cv2.inRange(hsv, BLUE_MIN, BLUE_MAX)
            green_mask = cv2.inRange(hsv, GREEN_MIN, GREEN_MAX)
            yellow_mask = cv2.inRange(hsv, YELLOW_MIN, YELLOW_MAX)
            black_mask = cv2.inRange(hsv, BLACK_MIN, BLACK_MAX)
            
            blue_res = cv2.bitwise_and(right_frame, right_frame, mask=blue_mask)
            green_res = cv2.bitwise_and(right_frame, right_frame, mask=green_mask)
            yellow_res = cv2.bitwise_and(right_frame, right_frame, mask=yellow_mask)
            black_res = cv2.bitwise_xor(right_frame, right_frame, mask=black_mask)

            # cv2.imshow("Black Mask", black_mask)
            # cv2.imshow("Blue Filter", blue_res)
            # cv2.imshow("Green Filter", green_res)
            # cv2.imshow("Yellow Filter", yellow_res)
            # cv2.imshow("Black Filter", black_res)
            # cv2.waitKey(IMSHOW_WAIT)

            # Blurring frame to remove noise in the license plate outline frame
            blur_plate_frame = cv2.blur(black_mask, (3,3))
            # cv2.imshow("Blur Black Mask", blur_plate_frame)
            # cv2.waitKey(IMSHOW_WAIT)

            frame_array = np.asarray(blur_plate_frame)

            # Arrays that will count the nummber of pixels within a threshold for each row and column
            column_array = np.zeros(crop_width)
            row_array = np.zeros((crop_height))

            for x in range(crop_width):
                for y in range(crop_height):
                    if frame_array[y][x] > BINARY_THRESH:
                        column_array[x] += 1
                        row_array[y] += 1       

            # Filter out noise to only get the boundary of the license plates
            column_array = [0 if column_array_ < COLUMN_THRESH else int(column_array_) for column_array_ in column_array]
            row_array = [0 if row_array_ < ROW_THRESH else int(row_array_) for row_array_ in row_array]

    
            # Horizontal Bounds, look for left bound then right bound
            for i in range(crop_width):
                if column_array[i] > BOUNDARY_THRESH:
                    x_bound[0] = i
                    break

            for j in range(crop_width - 1, 0, -1):
                if column_array[j] > BOUNDARY_THRESH:
                    x_bound[1] = j
                    break


            # Vertical Bounds
            # Parking Plate
            for i in range(crop_height):
                if (parking_plate_y[0] == 0) and (row_array[i] > BOUNDARY_THRESH):
                        parking_plate_y[0] = i
                elif parking_plate_y[1] == 0:
                    if (i - parking_plate_y[0] > PLATE_Y_OFFSET) and (row_array[i] > BOUNDARY_THRESH):
                        parking_plate_y[1] = i
                
            # License Plate
            for j in range(crop_height - 1, 0 , -1):
                if (license_plate_y[0] == 0) and (row_array[j] > BOUNDARY_THRESH):
                        license_plate_y[0] = j
                elif license_plate_y[1] == 0:
                    if (license_plate_y[0] - j > PLATE_Y_OFFSET) and (row_array[j] > BOUNDARY_THRESH):
                        license_plate_y[1] = j

            if (x_bound[1] - x_bound[0] > X_MIN_SIZE) and (license_plate_y[1] - license_plate_y[0] > PLATE_MIN_SIZE or (parking_plate_y[1] - parking_plate_y[0] > PLATE_MIN_SIZE)):
                # Parking Plate Box
                cv2.line(right_frame,(x_bound[0],parking_plate_y[0]),(x_bound[1],parking_plate_y[0]), LINE_COLOUR, LINE_THICKNESS)
                cv2.line(right_frame,(x_bound[0],parking_plate_y[1]),(x_bound[1],parking_plate_y[1]), LINE_COLOUR, LINE_THICKNESS)
                cv2.line(right_frame,(x_bound[0],parking_plate_y[0]),(x_bound[0],parking_plate_y[1]), LINE_COLOUR, LINE_THICKNESS)
                cv2.line(right_frame,(x_bound[1],parking_plate_y[0]),(x_bound[1],parking_plate_y[1]), LINE_COLOUR, LINE_THICKNESS)


                # License Plate Box
                cv2.line(right_frame,(x_bound[0],license_plate_y[0]),(x_bound[1],license_plate_y[0]), LINE_COLOUR, LINE_THICKNESS)
                cv2.line(right_frame,(x_bound[0],license_plate_y[1]),(x_bound[1],license_plate_y[1]), LINE_COLOUR, LINE_THICKNESS)
                cv2.line(right_frame,(x_bound[0],license_plate_y[0]),(x_bound[0],license_plate_y[1]), LINE_COLOUR, LINE_THICKNESS)
                cv2.line(right_frame,(x_bound[1],license_plate_y[0]),(x_bound[1],license_plate_y[1]), LINE_COLOUR, LINE_THICKNESS)

            print("X-size: ", x_bound[1] - x_bound[0])
            print("License-size: ", license_plate_y[1] - license_plate_y[0])
            print("Parking-size: ", parking_plate_y[1] - parking_plate_y[0])
            
            cv2.imshow("Plate Detection", right_frame)
            cv2.waitKey(IMSHOW_WAIT)

if __name__ == "__main__":
    main()