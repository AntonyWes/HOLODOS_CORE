from api.api import HOLODOS_API
from state.state import load_state, save_state, generate_device_id, generate_pin, generate_token

STATE = load_state()

if not STATE["device_id"]:
    STATE["device_id"] = generate_device_id()
    STATE["pin"] = generate_pin()
    save_state(STATE)

API = HOLODOS_API(STATE)

print("=== HOLODOS ===")
print(f"Device ID: {STATE['device_id']}")
print(f"PIN: {STATE['pin']}")
print("QR code saved as pair_qr.png")
