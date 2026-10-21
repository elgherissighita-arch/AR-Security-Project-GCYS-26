"""
Soumaya - overlay test with the REAL webcam, using Hiba's detector and Ghita's get_info.
Run from the project root:  python overlay/test_overlay_webcam.py
Keys: click = select an object | a = alert on selected type | x = clear alerts | q = quit
(The mouse click replaces Asma's gesture selection for this test.)
"""
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
from overlay import draw_all, BoxSmoother
from detector import detect          # Hiba
from security import get_info        # Ghita

DETECT_EVERY = 2
smoother = BoxSmoother()
detections, selected_name, alert_names = [], None, set()


def on_mouse(event, x, y, flags, param):
    global selected_name
    if event != cv2.EVENT_LBUTTONDOWN:
        return
    hit = [d for d in detections if d["x1"] <= x <= d["x2"] and d["y1"] <= y <= d["y2"]]
    selected_name = min(hit, key=lambda d: (d["x2"] - d["x1"]) * (d["y2"] - d["y1"]))["name"] if hit else None


cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
if not cap.isOpened():
    cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError("Could not open the webcam (try index 1)")

cv2.namedWindow("Overlay + webcam")
cv2.setMouseCallback("Overlay + webcam", on_mouse)

n = 0
while True:
    ok, frame = cap.read()
    if not ok:
        break
    if n % DETECT_EVERY == 0:
        detections = smoother.update(detect(frame))
    n += 1

    sel_index = next((i for i, d in enumerate(detections) if d["name"] == selected_name), None)
    draw_all(frame, detections, get_info, selected_index=sel_index, alert_names=alert_names)
    cv2.imshow("Overlay + webcam", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
    elif key == ord("a") and selected_name:
        alert_names ^= {selected_name}       # toggle
    elif key == ord("x"):
        alert_names.clear()

cap.release()
cv2.destroyAllWindows()