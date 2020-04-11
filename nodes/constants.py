import numpy as np

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

IMSHOW_WAIT = 3

LINE_COLOUR = (105, 255, 180)
LINE_THICKNESS = 1
CIRCLE_THICKNESS = 2
CIRCLE_RADIUS = 7
