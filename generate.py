# step 1: make fake satellite images where we know the true pose
import os
import csv
import cv2
import numpy as np
import satellite as sat

NUM_IMAGES = 50

os.makedirs("images", exist_ok=True)
np.random.seed(42)

truth_file = open("truth.csv", "w", newline="")
writer = csv.writer(truth_file)
writer.writerow(["image", "rx", "ry", "rz", "tx", "ty", "tz"])

for i in range(NUM_IMAGES):
    # random rotation (radians) and position (meters)
    rvec = np.random.uniform(-0.8, 0.8, 3)
    tx = np.random.uniform(-1.0, 1.0)
    ty = np.random.uniform(-0.7, 0.7)
    tz = np.random.uniform(7.0, 12.0)
    tvec = np.array([tx, ty, tz])

    # black space background with random stars
    img = np.zeros((sat.HEIGHT, sat.WIDTH, 3), dtype=np.uint8)
    for s in range(80):
        x = np.random.randint(0, sat.WIDTH)
        y = np.random.randint(0, sat.HEIGHT)
        brightness = np.random.randint(100, 256)
        cv2.circle(img, (x, y), 1, (brightness, brightness, brightness), -1)

    # draw the solar panels (dark blue)
    proj = cv2.projectPoints(sat.PANEL_RIGHT_3D, rvec, tvec, sat.CAMERA, sat.DIST)
    pts = proj[0].reshape(-1, 2).astype(np.int32)
    cv2.fillConvexPoly(img, pts, (110, 40, 20))
    proj = cv2.projectPoints(sat.PANEL_LEFT_3D, rvec, tvec, sat.CAMERA, sat.DIST)
    pts = proj[0].reshape(-1, 2).astype(np.int32)
    cv2.fillConvexPoly(img, pts, (110, 40, 20))

    # draw the body (gray)
    proj = cv2.projectPoints(sat.BODY_3D, rvec, tvec, sat.CAMERA, sat.DIST)
    pts = proj[0].reshape(-1, 2).astype(np.int32)
    hull = cv2.convexHull(pts)
    cv2.fillConvexPoly(img, hull, (130, 130, 130))

    # draw the colored markers
    proj = cv2.projectPoints(sat.MARKERS_3D, rvec, tvec, sat.CAMERA, sat.DIST)
    pts = proj[0].reshape(-1, 2)
    for m in range(len(pts)):
        center = (int(round(pts[m][0])), int(round(pts[m][1])))
        cv2.circle(img, center, 5, sat.MARKER_COLORS[m], -1)

    # make it look more like a real camera: blur + noise
    img = cv2.GaussianBlur(img, (3, 3), 0)
    noise = np.random.normal(0, 8, img.shape)
    img = np.clip(img.astype(np.float64) + noise, 0, 255).astype(np.uint8)

    name = "img_" + str(i).zfill(3) + ".png"
    cv2.imwrite(os.path.join("images", name), img)
    writer.writerow([name, rvec[0], rvec[1], rvec[2], tx, ty, tz])

truth_file.close()
print("made", NUM_IMAGES, "images in images/ and saved true poses to truth.csv")
