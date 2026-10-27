"""
Security rules for the EXAM ROOM scenario.
"""

SECURITY_RULES = {
    "person":     {"role": "student / invigilator", "risk_score": 5,  "status": "Allowed",
                   "description": "Person present in the exam room"},
    "bottle":     {"role": "personal item", "risk_score": 20, "status": "Allowed",
                   "description": "Water bottle is allowed in the exam room"},
    "cup":        {"role": "personal item", "risk_score": 20, "status": "Allowed",
                   "description": "Cup is allowed in the exam room"},
    "backpack":   {"role": "bag to inspect", "risk_score": 50, "status": "Inspection required",
                   "description": "Bags must be inspected and left at the front"},
    "cell phone": {"role": "cheating device", "risk_score": 95, "status": "Not allowed",
                   "description": "Phones are forbidden during the exam"},
    "laptop":     {"role": "cheating device", "risk_score": 85, "status": "Not allowed",
                   "description": "Laptops are forbidden during the exam"},
    "keyboard":   {"role": "electronic device", "risk_score": 70, "status": "Not allowed",
                   "description": "Electronic devices are forbidden"},
    "mouse":      {"role": "electronic device", "risk_score": 70, "status": "Not allowed",
                   "description": "Electronic devices are forbidden"},
    "tv":         {"role": "electronic device", "risk_score": 70, "status": "Not allowed",
                   "description": "Screens are forbidden during the exam"},
    "book":       {"role": "notes / documents", "risk_score": 75, "status": "Not allowed",
                   "description": "Books and notes are forbidden during the exam"},
}

DEFAULT_INFO = {
    "role": "unknown",
    "risk_score": 0,
    "status": "Unknown",
    "description": "No security information available",
}


def get_info(name):
    return SECURITY_RULES.get(name, DEFAULT_INFO)


def check_object(detected_object):
    name = detected_object["name"]
    info = get_info(name)
    return {
        "name": name,
        "confidence": detected_object.get("confidence", 0),
        "status": info["status"],
        "risk_score": info["risk_score"],
        "role": info["role"],
        "description": info["description"],
    }