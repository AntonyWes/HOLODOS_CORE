import json
import secrets
import string
from pathlib import Path

STATE_FILE = Path("state/state.json")

def load_state():
    if not STATE_FILE.exists():
        return {
            "paired": False,
            "device_id": None,
            "pin": None,
            "api_token": None,
            "target_temperature": None
        }
    else:
        return json.loads(STATE_FILE.read_text())
    
def save_state(state):
    STATE_FILE.parent.mkdir(exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))

def generate_pin():
    return "".join(secrets.choice(string.digits) for _ in range(6))

def generate_device_id():
    return "holodos-" + secrets.token_hex(3)

def generate_token():
    return secrets.token_urlsafe(32)