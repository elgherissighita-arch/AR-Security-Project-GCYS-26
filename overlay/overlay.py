"""
Module 2 - AR Overlay (Soumaya)

Draws the virtual cybersecurity interface on top of a camera frame.
Main function:  draw_overlay(frame, detection, info, selected=False, alert=False)
"""
import time

import cv2

# OpenCV colors are BGR (not RGB)
STATUS_COLORS = {
    "secure": (40, 180, 40),        # green
    "vulnerable": (0, 165, 255),    # orange
    "compromised": (0, 0, 230),     # red
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
    detection : {"name", "confidence", "x1", "y1", "x2", "y2"}   (from Hiba)
    info      : {"role", "status", "risk_score", "description"}  (from Ghita)
    selected  : True -> show the details panel                   (from Asma)
    alert     : True -> red blinking alert (simulated attack)
    """
    h, w = frame.shape[:2]
    x1, y1 = max(int(detection["x1"]), 0), max(int(detection["y1"]), 0)
    x2, y2 = min(int(detection["x2"]), w - 1), min(int(detection["y2"]), h - 1)

    status = "compromised" if alert else str(info.get("status", "secure")).lower()
    risk = max(0, min(100, int(info.get("risk_score", 0))))
    color = STATUS_COLORS.get(status, DEFAULT_COLOR)

    # 1. bounding box (thicker when selected / alert)
    thickness = 4 if (selected or alert) else 2
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)

    # 2. label: name + risk
    _draw_label(frame, x1, y1, f"{detection['name']} | Risk {risk}/100", color)

    # 3. status dot (top-right corner of the box)
    cv2.circle(frame, (x2 - 14, y1 + 14), 8, color, -1)
    cv2.circle(frame, (x2 - 14, y1 + 14), 8, WHITE, 1)

    # 4. details panel
    if selected:
        _draw_panel(frame, (x1, y1, x2, y2), detection, info, status, risk, color)

    # 5. alert effect: blinking red tint + warning banner
    if alert:
        if int(time.time() * 2) % 2 == 0:
            _fill_transparent(frame, (x1, y1), (x2, y2), STATUS_COLORS["compromised"], 0.25)
        _fill_transparent(frame, (x1, y2 - 30), (x2, y2), STATUS_COLORS["compromised"], 0.9)
        _text(frame, "ALERT: DEVICE COMPROMISED", (x1 + 8, y2 - 10), 0.5, WHITE, 2)

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