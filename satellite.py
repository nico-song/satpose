# shared settings for the fake satellite and the camera
import numpy as np

# image size
WIDTH = 640
HEIGHT = 480

# camera matrix (focal length 800 px, center of image)
CAMERA = np.array([
    [800.0, 0.0, 320.0],
    [0.0, 800.0, 240.0],
    [0.0, 0.0, 1.0]
])

# no lens distortion
DIST = np.zeros(5)

# 3d spots on the satellite where colored markers sit (meters)
# 4 on the corners of the body cube, 2 on the tips of the solar panels
MARKERS_3D = np.array([
    [0.5, 0.5, 0.5],
    [-0.5, 0.5, -0.5],
    [0.5, -0.5, -0.5],
    [-0.5, -0.5, 0.5],
    [1.8, 0.0, 0.0],
    [-1.8, 0.0, 0.0]
])

# marker colors in BGR (opencv order), same order as MARKERS_3D
MARKER_COLORS = [
    (0, 0, 255),      # red
    (0, 128, 255),    # orange
    (0, 255, 255),    # yellow
    (0, 255, 0),      # green
    (255, 255, 0),    # cyan
    (255, 0, 255)     # magenta
]

MARKER_NAMES = ["red", "orange", "yellow", "green", "cyan", "magenta"]

# hue range for each marker in HSV (opencv hue goes 0 to 179)
HUE_LOW = [0, 10, 25, 50, 80, 140]
HUE_HIGH = [6, 20, 35, 70, 100, 160]

# corners of the body cube
BODY_3D = np.array([
    [0.5, 0.5, 0.5], [0.5, 0.5, -0.5], [0.5, -0.5, 0.5], [0.5, -0.5, -0.5],
    [-0.5, 0.5, 0.5], [-0.5, 0.5, -0.5], [-0.5, -0.5, 0.5], [-0.5, -0.5, -0.5]
])

# corners of the two solar panels
PANEL_RIGHT_3D = np.array([
    [0.5, -0.3, 0.0], [1.8, -0.3, 0.0], [1.8, 0.3, 0.0], [0.5, 0.3, 0.0]
])
PANEL_LEFT_3D = np.array([
    [-0.5, -0.3, 0.0], [-1.8, -0.3, 0.0], [-1.8, 0.3, 0.0], [-0.5, 0.3, 0.0]
])
