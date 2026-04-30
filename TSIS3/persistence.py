import json
import os

LB_FILE  = "leaderboard.json"
SET_FILE = "settings.json"


def load_lb():
    if os.path.exists(LB_FILE):
        with open(LB_FILE) as f:
            return json.load(f)
    return []


def save_lb(name, score, dist):
    data = load_lb()
    data.append({"name": name, "score": score, "dist": int(dist)})
    data.sort(key=lambda x: x["score"], reverse=True)
    with open(LB_FILE, "w") as f:
        json.dump(data[:10], f, indent=2)


def load_settings():
    if os.path.exists(SET_FILE):
        return json.load(open(SET_FILE))
    return {"difficulty": "normal"}


def save_settings(s):
    json.dump(s, open(SET_FILE, "w"), indent=2)