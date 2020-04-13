import numpy as np
import cv2

# HSV values organized by [Hue, Saturation, Value]. Hue is the colour shade, saturation is of strong
# that colour is, and value is how bright it is
YELLOW_MIN = np.array([10, 50, 0])
YELLOW_MAX = np.array([40, 255, 255])
BLUE_MIN = np.array([100, 120, 0])
BLUE_MAX = np.array([120, 255, 255])
GREEN_MIN = np.array([50, 50, 0])
GREEN_MAX = np.array([70, 255, 255])
BLACK_MIN = np.array([0, 0, 0])
BLACK_MAX = np.array([255, 255, 50])

CONTOUR_AREA_MIN = 1750
CONTOUR_MIN_Y_DIST = 40
MAX_CONTOURS = 2
CORNERS_NEEDED = 9
PLATE_HEIGHT = 100
PLATE_WIDTH = 200
PLATE_DIM = (PLATE_WIDTH, PLATE_HEIGHT)

IMSHOW_WAIT = 3

LINE_COLOUR = (105, 255, 180)
LINE_THICKNESS = 1
CIRCLE_THICKNESS = 2
CIRCLE_RADIUS = 7
PARKING_HUD = (0, 30)
LICENSE_HUD = (0, 60)
FONT = cv2.FONT_HERSHEY_TRIPLEX
FONT_SCALE = 1
TEXT_COLOUR = (255, 255, 255)

# Location of characters on the plates
CROP_SIZE = (100, 50, 3)
LCHAR0 = (10, 0, 60, 100)
LCHAR1 = (55, 0, 105, 100)
LCHAR2 = (100, 0, 150, 100)
LCHAR3 = (140, 0, 190, 100)
LICENSE_CHAR = [LCHAR0, LCHAR1, LCHAR2, LCHAR3]

PCHAR0 = (35, 0, 85, 100)
PCHAR1 = (75, 0, 125, 100)
PCHAR2 = (120, 0, 170, 100)
PARKING_CHAR = [PCHAR0, PCHAR1, PCHAR2]
