
from detection import detect
from security import check_object
import cv2
from datetime import datetime

VIDEO_PATH = "demo.mp4"
LOG_FILE = "security_log.txt"

cap = cv2.VideoCapture(VIDEO_PATH)

if not cap.isOpened():
    print("ERROR: Cannot open video.")
    raise SystemExit

fps = cap.get(cv2.CAP_PROP_FPS)
if fps <= 0:
    fps = 25

delay = max(1, int(1000 / fps))
alerted_objects = set()

print("Security video analysis started.")
print("Press Q to quit.")

with open(LOG_FILE, "w", encoding="utf-8") as log:
    log.write("=== AR Security Event Log ===\n")

while True:
    ret, frame = cap.read()

    if not ret:
        print("End of video reached.")
        break

    detections = detect(frame)

    for obj in detections:
        result = check_object(obj)

        name = result["name"]
        status = result["status"]
        risk = result["risk_score"]
        confidence = result["confidence"]

        x1, y1 = obj["x1"], obj["y1"]
        x2, y2 = obj["x2"], obj["y2"]

        color = (0, 255, 0) if status == "Allowed" else (0, 0, 255)

        label = f"{name} | {status} | Risk: {risk}"

        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(
            frame, label,
            (x1, max(y1 - 10, 20)),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2
        )

        if status != "Allowed" and name not in alerted_objects:
            alerted_objects.add(name)

            alert = (
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
                f"ALERT | {name} | {status} | Risk: {risk} | "
                f"Confidence: {confidence}"
            )

            print(alert)

            with open(LOG_FILE, "a", encoding="utf-8") as log:
                log.write(alert + "\n")

    cv2.imshow("AR Security Surveillance", frame)

    if cv2.waitKey(delay) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()

print("Video analysis completed.")
print("Alerts saved in", LOG_FILE)
