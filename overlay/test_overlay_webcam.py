"""
Soumaya - overlay + ROOM SCAN with the REAL webcam.
Run from the project root:  python overlay/test_overlay_webcam.py
Keys: click = select | a = alert on selected | f = alert on all | x = clear alerts
      s = screenshot | q = quit
"""
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
from overlay import draw_all, BoxSmoother, draw_scan_summary, classify
import detector
from ultralytics import YOLO
from detector import detect          # Hiba
from security import get_info        # Ghita

detector.MIN_CONFIDENCE = 0.25            # accept weaker detections
detector.model = YOLO("yolov8s.pt")       # bigger, more accurate model

DETECT_EVERY = 2
os.makedirs("outputs", exist_ok=True)
smoother = BoxSmoother()
detections, selected_name, alert_names = [], None, set()
seen = {}


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

    counts = {}
    for d in detections:
        counts[d["name"]] = counts.get(d["name"], 0) + 1
    for k, v in counts.items():
        seen[k] = max(seen.get(k, 0), v)

    sel_index = next((i for i, d in enumerate(detections) if d["name"] == selected_name), None)
    draw_all(frame, detections, get_info, selected_index=sel_index, alert_names=alert_names)
    draw_scan_summary(frame, detections, get_info)
    cv2.imshow("Overlay + webcam", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
    elif key == ord("a") and selected_name:
        alert_names ^= {selected_name}
    elif key == ord("f"):
        alert_names = {d["name"] for d in detections}
    elif key == ord("x"):
        alert_names.clear()
    elif key == ord("s"):
        cv2.imwrite("outputs/overlay_screenshot.png", frame)
        print("Saved outputs/overlay_screenshot.png")

cap.release()
cv2.destroyAllWindows()

print("\n===== SCAN REPORT =====")
for name, count in sorted(seen.items()):
    info = get_info(name)
    print(f"{name:12s} x{count:<2d} {classify(info['status']):13s} risk {info['risk_score']}")