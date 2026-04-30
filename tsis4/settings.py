# settings.py
import json, os

FILE = os.path.join(os.path.dirname(__file__), "settings.json")

DEFAULTS = {
    "snake_color": [50, 200, 50],
    "grid":        True,
    "sound":       True,
}

def load():
    if os.path.exists(FILE):
        try:
            data = json.load(open(FILE))
            for k, v in DEFAULTS.items():
                data.setdefault(k, v)
            return data
        except Exception:
            pass
    return dict(DEFAULTS)

def save(s):
    json.dump(s, open(FILE, "w"), indent=2)