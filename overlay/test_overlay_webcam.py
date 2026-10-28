"""
Soumaya and Asma - overlay + ROOM SCAN with the REAL webcam.
Run from the project root:  python overlay/test_overlay_webcam.py
Keys: click = select | a = alert on selected | f = alert on all | x = clear alerts
      d = show/hide debug line | s = screenshot | q = quit
"""
import os
import sys
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
from overlay import draw_all, BoxSmoother, draw_scan_summary, classify
import detector
from ultralytics import YOLO
from detector import detect
from security import get_info

detector.MIN_CONFIDENCE = 0.30
detector.model = YOLO("yolov8m.pt")       # bigger model = more accurate (slower)
# stricter threshold for the class the model confuses most (a mouse looks like a phone)
MIN_CONF = {"cell phone": 0.75}

DETECT_EVERY = 3
os.makedirs("outputs", exist_ok=True)
smoother = BoxSmoother()
detections, selected_name, alert_names = [], None, set()
seen, raw_text, show_debug = {}, "YOLO sees: ...", False


def iou(a, b):
    """Overlap between two detections (0 = none, 1 = identical boxes)."""
    ix1, iy1 = max(a["x1"], b["x1"]), max(a["y1"], b["y1"])
    ix2, iy2 = min(a["x2"], b["x2"]), min(a["y2"], b["y2"])
    inter = max(0, ix2 - ix1) * max(0, iy2 - iy1)
    area_a = (a["x2"] - a["x1"]) * (a["y2"] - a["y1"])
    area_b = (b["x2"] - b["x1"]) * (b["y2"] - b["y1"])
    union = area_a + area_b - inter
    return inter / union if union > 0 else 0


def clean(dets):
    """Apply per-class thresholds, then if two different classes cover the same
    object, keep only the more confident one."""
    dets = [d for d in dets if d["confidence"] >= MIN_CONF.get(d["name"], 0.30)]
    dets.sort(key=lambda d: d["confidence"], reverse=True)
    kept = []
    for d in dets:
        if all(not (iou(d, k) > 0.5 and d["name"] != k["name"]) for k in kept):
            kept.append(d)
    return kept


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
    h, w = frame.shape[:2]

    if n % DETECT_EVERY == 0:
        detections = smoother.update(clean(detect(frame)))

    # debug (key d): what does YOLO see at all, every class, low confidence
    if show_debug and n % 10 == 0:
        res = detector.model(frame, conf=0.15, verbose=False)[0]
        raw = [f"{detector.model.names[int(b.cls[0])]} {float(b.conf[0]):.2f}" for b in res.boxes]
        raw_text = "YOLO sees: " + (", ".join(raw) if raw else "nothing")
    n += 1

    counts = {}
    for d in detections:
        counts[d["name"]] = counts.get(d["name"], 0) + 1
    for k, v in counts.items():
        seen[k] = max(seen.get(k, 0), v)

    sel_index = next((i for i, d in enumerate(detections) if d["name"] == selected_name), None)
    draw_all(frame, detections, get_info, selected_index=sel_index, alert_names=alert_names)
    draw_scan_summary(frame, detections, get_info)

    # big alert banner at the bottom when something unauthorized is detected
    unauth = [d for d in detections if classify(get_info(d["name"])["status"]) == "unauthorized"]
    if unauth and int(time.time() * 2) % 2 == 0:
        cv2.rectangle(frame, (0, h - 50), (w, h), (0, 0, 230), -1)
        cv2.putText(frame, f"!!! ALERT: {len(unauth)} UNAUTHORIZED ITEM(S) !!!", (20, h - 16),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2, cv2.LINE_AA)

    # debug line above the banner (hidden by default)
    if show_debug:
        cv2.rectangle(frame, (0, h - 80), (w, h - 52), (0, 0, 0), -1)
        cv2.putText(frame, raw_text[:90], (10, h - 59), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (0, 255, 255), 1, cv2.LINE_AA)

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
    elif key == ord("d"):
        show_debug = not show_debug
    elif key == ord("s"):
        cv2.imwrite("outputs/overlay_screenshot.png", frame)
        print("Saved outputs/overlay_screenshot.png")

cap.release()
cv2.destroyAllWindows()

print("\n===== SCAN REPORT =====")
for name, count in sorted(seen.items()):
    info = get_info(name)
    print(f"{name:12s} x{count:<2d} {classify(info['status']):13s} risk {info['risk_score']}")