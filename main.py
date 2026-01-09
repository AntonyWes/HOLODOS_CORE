import api.state_ref as ref
import uvicorn
import threading
import time
import random
from api.api import HOLODOS_API
from state.state import load_state, save_state, generate_device_id, generate_pin
from controllers.screen.screen import DisplayDriver, render


STATE = load_state()

if not STATE["paired"]:
    STATE["device_id"] = generate_device_id()
    STATE["pin"] = generate_pin()
    save_state(STATE)

print("=== HOLODOS ===")

ref.STATE = STATE

api = HOLODOS_API(STATE)
api.prepare_pairing()
api.print_info()

def display_update_worker(display_device):
    while True:
        STATE = load_state()

        temp = round(random.uniform(3.5, 4.5), 1)
        hum = random.randint(40, 50)
        is_open = random.random() > 0.9
        is_cooling = temp > int(STATE.get('target_temperature') or 4)

        img = render(
            temp=temp, 
            humidity=hum, 
            target=int(STATE.get('target_temperature') or 4), 
            is_cooling=is_cooling, 
            is_open=is_open,
            wifi_connected=STATE['paired']
        )

        try:
            display_device.show(img)
        except Exception as e:
            print(e)

        time.sleep(3)

if __name__ == "__main__":
    display = DisplayDriver()
    
    display_thread = threading.Thread(
        target=display_update_worker, 
        args=(display,),
        daemon=True
    )
    display_thread.start()

    uvicorn.run(
        "api.app:app",
        host="0.0.0.0",
        port=8080
    )
