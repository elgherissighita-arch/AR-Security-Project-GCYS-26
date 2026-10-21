"""
Soumaya - overlay on a VIDEO or an IMAGE file (instead of the webcam).
Run from the project root:
    python overlay/test_overlay_video.py demo.mp4
    python overlay/test_overlay_video.py images/photo.jpg
Keys: click = select | a = alert on selected | f = alert on all | x = clear alerts
      space = pause | s = screenshot | q = quit
The result video is saved to outputs/overlay_result.mp4
"""
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
from overlay import draw_all, BoxSmoother
from detector import detect          # Hiba
from security import get_info        # Ghita

if len(sys.argv) < 2:
    print("Usage: python overlay/test_overlay_video.py <video or image path>")
    sys.exit(1)



path = sys.argv[1]
is_image = path.lower().endswith((".jpg", ".jpeg", ".png"))
os.makedirs("outputs", exist_ok=True)

cap, image = None, None
if is_image:
    image = cv2.imread(path)
    if image is None:
        raise RuntimeError(f"Could not read image: {path}")
else:
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {path}")

smoother = BoxSmoother()
detections, selected_name, alert_names = [], None, set()
paused, writer, raw = False, None, None


def on_mouse(event, x, y, flags, param):
    global selected_name
    if event != cv2.EVENT_LBUTTONDOWN:
        return
    hit = [d for d in detections if d["x1"] <= x <= d["x2"] and d["y1"] <= y <= d["y2"]]
    selected_name = min(hit, key=lambda d: (d["x2"] - d["x1"]) * (d["y2"] - d["y1"]))["name"] if hit else None


cv2.namedWindow("Overlay + video")
cv2.setMouseCallback("Overlay + video", on_mouse)

while True:
    if is_image:
        if raw is None:
            raw = image.copy()
            detections = smoother.update(detect(raw))
    elif not paused:
        ok, raw = cap.read()
        if not ok:
            print("End of video.")
            break
        detections = smoother.update(detect(raw))

    frame = raw.copy()
    sel_index = next((i for i, d in enumerate(detections) if d["name"] == selected_name), None)
    draw_all(frame, detections, get_info, selected_index=sel_index, alert_names=alert_names)

    if not is_image and not paused:
        if writer is None:
            h, w = frame.shape[:2]
            fps = cap.get(cv2.CAP_PROP_FPS) or 25
            writer = cv2.VideoWriter("outputs/overlay_result.mp4",
                                     cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
        writer.write(frame)

    cv2.imshow("Overlay + video", frame)
    key = cv2.waitKey(1 if not is_image else 30) & 0xFF
    if key == ord("q"):
        break
    elif key == ord(" "):
        paused = not paused
    elif key == ord("a") and selected_name:
        alert_names ^= {selected_name}
    elif key == ord("f"):
        alert_names = {d["name"] for d in detections}
    elif key == ord("x"):
        alert_names.clear()
    elif key == ord("s"):
        cv2.imwrite("outputs/overlay_screenshot.png", frame)
        print("Saved outputs/overlay_screenshot.png")

if cap:
    cap.release()
if writer:
    writer.release()
    print("Saved outputs/overlay_result.mp4")
cv2.destroyAllWindows()