import cv2
import numpy as np

from overlay import draw_overlay

# Fake detection (this will come from Hiba) and fake info (from Ghita)
detection = {"name": "laptop", "confidence": 0.94, "x1": 80, "y1": 120, "x2": 400, "y2": 380}
info = {
    "role": "Workstation",
    "status": "vulnerable",
    "risk_score": 65,
    "description": "Security update required",
}

# Keys: s = selected panel on/off, a = alert on/off, 1/2/3 = secure/vulnerable/compromised, q = quit
selected, alert = True, False

while True:
    frame = np.full((520, 900, 3), 65, dtype=np.uint8)   # fake camera image
    draw_overlay(frame, detection, info, selected=selected, alert=alert)
    cv2.imshow("Overlay test", frame)

    key = cv2.waitKey(50) & 0xFF
    if key == ord("q"):
        break
    elif key == ord("s"):
        selected = not selected
    elif key == ord("a"):
        alert = not alert
    elif key in (ord("1"), ord("2"), ord("3")):
        info["status"] = ["secure", "vulnerable", "compromised"][key - ord("1")]
        info["risk_score"] = [15, 65, 95][key - ord("1")]

cv2.destroyAllWindows()