import json

# Load security data
with open("security_data.json", "r") as file:
    security_data = json.load(file)


def get_info(name):
    return security_data.get(
        name,
        {
            "role": "unknown",
            "risk_score": 0,
            "status": "Unknown",
            "description": "No security information available"
        }
    )
def check_object(detected_object):
    name = detected_object["name"]
    info = get_info(name)

    return {
        "name": name,
        "confidence": detected_object.get("confidence", 0),
        "status": info["status"],
        "risk_score": info["risk_score"],
        "role": info["role"],
        "description": info["description"]
    }