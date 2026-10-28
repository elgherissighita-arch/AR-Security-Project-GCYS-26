"""
Module 2 - AR Overlay (Soumaya and Asma)

Draws the virtual cybersecurity interface on top of a camera frame.
Main function:  draw_overlay(frame, detection, info, selected=False, alert=False)
"""
import time

import cv2

# OpenCV colors are BGR (not RGB)
STATUS_COLORS = {
    "secure": (40, 180, 40),
    "allowed": (40, 180, 40),                # green
    "vulnerable": (0, 165, 255),
    "warning": (0, 165, 255),
    "inspection required": (0, 165, 255),    # orange
    "compromised": (0, 0, 230),
    "restricted": (0, 0, 230),
    "not allowed": (0, 0, 230),              # red
}
DEFAULT_COLOR = (180, 180, 180)
WHITE = (255, 255, 255)
FONT = cv2.FONT_HERSHEY_SIMPLEX


def _fill_transparent(frame, p1, p2, color, alpha=0.65):
    """Draw a semi-transparent filled rectangle (clipped to the frame)."""
    h, w = frame.shape[:2]
    x1, y1 = max(p1[0], 0), max(p1[1], 0)
    x2, y2 = min(p2[0], w - 1), min(p2[1], h - 1)
    if x2 <= x1 or y2 <= y1:
        return
    roi = frame[y1:y2, x1:x2]
    block = roi.copy()
    block[:] = color
    cv2.addWeighted(block, alpha, roi, 1 - alpha, 0, roi)


def _text(frame, text, org, scale=0.5, color=WHITE, thickness=1):
    cv2.putText(frame, text, org, FONT, scale, color, thickness, cv2.LINE_AA)


def _draw_label(frame, x1, y1, text, color):
    """Name + risk tag just above the box (or inside it if the box touches the top)."""
    (tw, th), _ = cv2.getTextSize(text, FONT, 0.55, 1)
    pad = 6
    top = y1 - th - 2 * pad
    if top < 0:
        top = y1
    _fill_transparent(frame, (x1, top), (x1 + tw + 2 * pad, top + th + 2 * pad), color, 0.85)
    _text(frame, text, (x1 + pad, top + th + pad - 1), 0.55)


def _draw_panel(frame, box, detection, info, status, risk, color):
    """Details panel, placed to the right of the object (or left if no room)."""
    h, w = frame.shape[:2]
    x1, y1, x2, y2 = box
    pw, ph = 270, 165

    px = x2 + 12
    if px + pw > w:                 # not enough room on the right
        px = x1 - pw - 12
    px = min(max(px, 0), max(w - pw, 0))
    py = min(max(y1, 0), max(h - ph, 0))

    _fill_transparent(frame, (px, py), (px + pw, py + ph), (30, 30, 30), 0.75)
    cv2.rectangle(frame, (px, py), (px + pw, py + ph), color, 2)

    x = px + 12
    _text(frame, detection["name"].upper(), (x, py + 26), 0.7, WHITE, 2)
    _text(frame, f"Role: {info.get('role', 'Unknown')}", (x, py + 52))
    _text(frame, f"Status: {status.upper()}", (x, py + 74), 0.5, color, 1)
    _text(frame, f"Risk score: {risk}/100", (x, py + 96))

    # risk bar
    bx, by, bw, bh = x, py + 104, pw - 24, 10
    cv2.rectangle(frame, (bx, by), (bx + bw, by + bh), (90, 90, 90), -1)
    cv2.rectangle(frame, (bx, by), (bx + int(bw * risk / 100), by + bh), color, -1)

    desc = str(info.get("description", ""))
    _text(frame, desc[:34], (x, py + 138), 0.45, (220, 220, 220))
    if len(desc) > 34:
        _text(frame, desc[34:68], (x, py + 154), 0.45, (220, 220, 220))


def draw_overlay(frame, detection, info, selected=False, alert=False):
    """
    frame     : BGR image from the webcam (modified in place and returned)
    detection : {"name", "confidence", "x1", "y1", "x2", "y2"}   (from the detector)
    info      : {"role", "status", "risk_score", "description"}  (from the security rules)
    selected  : True -> show the details panel                   (object clicked by the user)
    alert     : True -> red blinking alert (simulated attack)
    """
    h, w = frame.shape[:2]
    x1, y1 = max(int(detection["x1"]), 0), max(int(detection["y1"]), 0)
    x2, y2 = min(int(detection["x2"]), w - 1), min(int(detection["y2"]), h - 1)

    if classify(info.get("status", "")) == "unauthorized":
        alert = True        # unauthorized items always trigger the alert
    status = "compromised" if alert else str(info.get("status", "secure")).lower()
    risk = max(0, min(100, int(info.get("risk_score", 0))))
    color = STATUS_COLORS.get(status, DEFAULT_COLOR)

    # 1. bounding box (thicker when selected / alert)
    thickness = 4 if (selected or alert) else 2
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)

    # 2. label: name + confidence + risk
    conf = int(detection.get("confidence", 0) * 100)
    _draw_label(frame, x1, y1, f"{detection['name']} {conf}% | Risk {risk}/100", color)

    # 3. status dot (top-right corner of the box)
    cv2.circle(frame, (x2 - 14, y1 + 14), 8, color, -1)
    cv2.circle(frame, (x2 - 14, y1 + 14), 8, WHITE, 1)

    # 4. details panel
    if selected:
        _draw_panel(frame, (x1, y1, x2, y2), detection, info, status, risk, color)

    # 5. alert effect: blinking red tint + white border + warning banner
    if alert:
        if int(time.time() * 2) % 2 == 0:
            _fill_transparent(frame, (x1, y1), (x2, y2), STATUS_COLORS["compromised"], 0.4)
            cv2.rectangle(frame, (x1, y1), (x2, y2), WHITE, 2)
        _fill_transparent(frame, (x1, y2 - 36), (x2, y2), STATUS_COLORS["compromised"], 0.95)
        _text(frame, "! ALERT: UNAUTHORIZED ITEM", (x1 + 8, y2 - 12), 0.55, WHITE, 2)

    return frame


def draw_all(frame, detections, get_info, selected_index=None, alert_names=()):
    """Helper for main.py: draw an overlay for every detection in the list."""
    for i, det in enumerate(detections):
        draw_overlay(
            frame, det, get_info(det["name"]),
            selected=(i == selected_index),
            alert=(det["name"] in alert_names),
        )
    return frame


class BoxSmoother:
    """
    Removes flickering: averages each box position over the last frames.
    Usage:  smoother = BoxSmoother()
            smooth_dets = smoother.update(detections)   # call each time YOLO runs
    """
    def __init__(self, alpha=0.4, max_dist=120, max_missing=5):
        self.alpha = alpha              # lower = smoother but slower to follow
        self.max_dist = max_dist        # max pixel jump to be the same object
        self.max_missing = max_missing  # keep an object this many updates after it disappears
        self.tracks = []

    def update(self, detections):
        for t in self.tracks:
            t["seen"] = False
        out = []
        for det in detections:
            box = [det["x1"], det["y1"], det["x2"], det["y2"]]
            cx, cy = (box[0] + box[2]) / 2, (box[1] + box[3]) / 2
            best, best_d = None, self.max_dist
            for t in self.tracks:
                if t["seen"] or t["name"] != det["name"]:
                    continue
                tx = (t["box"][0] + t["box"][2]) / 2
                ty = (t["box"][1] + t["box"][3]) / 2
                d = ((cx - tx) ** 2 + (cy - ty) ** 2) ** 0.5
                if d < best_d:
                    best, best_d = t, d
            if best is None:
                best = {"name": det["name"], "box": box, "seen": True, "missing": 0}
                self.tracks.append(best)
            else:
                a = self.alpha
                best["box"] = [a * n + (1 - a) * o for n, o in zip(box, best["box"])]
                best["seen"], best["missing"] = True, 0
            smoothed = dict(det)
            smoothed["x1"], smoothed["y1"], smoothed["x2"], smoothed["y2"] = (int(v) for v in best["box"])
            out.append(smoothed)
        for t in self.tracks:
            if not t["seen"]:
                t["missing"] += 1
        self.tracks = [t for t in self.tracks if t["missing"] <= self.max_missing]
        return out


def classify(status):
    """Turn a security status into one of 3 scan categories."""
    s = str(status).lower()
    if s in ("secure", "allowed"):
        return "authorized"
    if s in ("vulnerable", "warning", "inspection required"):
        return "to inspect"
    if s in ("compromised", "restricted", "not allowed"):
        return "unauthorized"
    return "unknown"


def draw_scan_summary(frame, detections, get_info):
    """Top-left panel: room scan result (counts + overall room status)."""
    counts = {"authorized": 0, "to inspect": 0, "unauthorized": 0, "unknown": 0}
    for det in detections:
        counts[classify(get_info(det["name"]).get("status", ""))] += 1

    if counts["unauthorized"] > 0:
        room, room_color = "ROOM: VIOLATION", STATUS_COLORS["compromised"]
    elif counts["to inspect"] > 0:
        room, room_color = "ROOM: CHECK NEEDED", STATUS_COLORS["vulnerable"]
    else:
        room, room_color = "ROOM: CLEAR", STATUS_COLORS["secure"]

    x, y, w, h = 10, 10, 250, 135
    _fill_transparent(frame, (x, y), (x + w, y + h), (30, 30, 30), 0.75)
    cv2.rectangle(frame, (x, y), (x + w, y + h), room_color, 2)
    _text(frame, "ROOM SCAN", (x + 12, y + 26), 0.65, WHITE, 2)
    _text(frame, f"Objects detected: {len(detections)}", (x + 12, y + 50))
    _text(frame, f"Authorized: {counts['authorized']}", (x + 12, y + 70), 0.5, STATUS_COLORS["secure"])
    _text(frame, f"To inspect: {counts['to inspect']}", (x + 12, y + 88), 0.5, STATUS_COLORS["vulnerable"])
    _text(frame, f"Unauthorized: {counts['unauthorized']}", (x + 12, y + 106), 0.5, STATUS_COLORS["compromised"])
    _text(frame, room, (x + 12, y + 128), 0.55, room_color, 2)
    return frame