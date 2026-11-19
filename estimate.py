# step 2: find the markers in each image, estimate the pose, and check how close we got
import os
import csv
import math
import cv2
import numpy as np
import satellite as sat

os.makedirs("output", exist_ok=True)

# read the true poses
truth = {}
truth_file = open("truth.csv")
reader = csv.DictReader(truth_file)
for row in reader:
    truth[row["image"]] = row
truth_file.close()

results_file = open("results.csv", "w", newline="")
writer = csv.writer(results_file)
writer.writerow(["image", "markers_found", "position_error_m", "rotation_error_deg"])

all_pos_errors = []
all_rot_errors = []
skipped = 0

for name in sorted(truth.keys()):
    img = cv2.imread(os.path.join("images", name))

    # preprocessing: blur to smooth out noise, then switch to HSV so colors are easy to pick out
    smooth = cv2.GaussianBlur(img, (5, 5), 0)
    hsv = cv2.cvtColor(smooth, cv2.COLOR_BGR2HSV)

    # detection: find each colored marker
    found_2d = []
    found_3d = []
    for m in range(len(sat.MARKER_NAMES)):
        low = np.array([sat.HUE_LOW[m], 120, 150])
        high = np.array([sat.HUE_HIGH[m], 255, 255])
        mask = cv2.inRange(hsv, low, high)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))

        contours = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
        if len(contours) == 0:
            continue

        # biggest blob of that color = the marker
        biggest = max(contours, key=cv2.contourArea)
        moments = cv2.moments(biggest)
        if moments["m00"] == 0:
            continue
        cx = moments["m10"] / moments["m00"]
        cy = moments["m01"] / moments["m00"]
        found_2d.append([cx, cy])
        found_3d.append(sat.MARKERS_3D[m])

    # need at least 4 points to solve for pose
    if len(found_2d) < 4:
        print(name, "only found", len(found_2d), "markers, skipping")
        writer.writerow([name, len(found_2d), "", ""])
        skipped = skipped + 1
        continue

    # pose estimation
    pnp = cv2.solvePnP(np.array(found_3d), np.array(found_2d), sat.CAMERA, sat.DIST,
                       flags=cv2.SOLVEPNP_SQPNP)
    rvec = pnp[1]
    tvec = pnp[2]

    # compare to the true pose
    t = truth[name]
    true_rvec = np.array([float(t["rx"]), float(t["ry"]), float(t["rz"])])
    true_tvec = np.array([float(t["tx"]), float(t["ty"]), float(t["tz"])])

    pos_error = np.linalg.norm(tvec.flatten() - true_tvec)

    est_R = cv2.Rodrigues(rvec)[0]
    true_R = cv2.Rodrigues(true_rvec)[0]
    diff = est_R.T @ true_R
    cos_angle = (np.trace(diff) - 1) / 2
    cos_angle = min(1.0, max(-1.0, cos_angle))
    rot_error = math.degrees(math.acos(cos_angle))

    all_pos_errors.append(pos_error)
    all_rot_errors.append(rot_error)
    writer.writerow([name, len(found_2d), round(pos_error, 4), round(rot_error, 3)])

    # save a picture with the estimated axes drawn on the satellite
    out = img.copy()
    for p in found_2d:
        cv2.circle(out, (int(p[0]), int(p[1])), 9, (255, 255, 255), 1)
    cv2.drawFrameAxes(out, sat.CAMERA, sat.DIST, rvec, tvec, 1.0, 2)
    cv2.imwrite(os.path.join("output", name), out)

results_file.close()

print("images solved:", len(all_pos_errors), " skipped:", skipped)
print("mean position error:", round(np.mean(all_pos_errors) * 100, 2), "cm")
print("mean rotation error:", round(np.mean(all_rot_errors), 3), "degrees")
print("worst rotation error:", round(np.max(all_rot_errors), 3), "degrees")
print("per-image results saved to results.csv, pictures saved to output/")
