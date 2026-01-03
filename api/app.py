from fastapi import FastAPI, HTTPException, Header
from state.state import load_state, save_state, generate_token

app = FastAPI()
state = load_state()

@app.get("/api/status")
def status():
    return {
        "paired": state["paired"],
        "device_id": state["device_id"],
        "target_temperature": state["target_temperature"]
    }

@app.post("/api/pair")
def pair(data: dict):
    if state["paired"]:
        raise HTTPException(400, "Already paired")

    if data.get("pin") != state["pin"]:
        raise HTTPException(401, "Invalid PIN")

    state["api_token"] = generate_token()
    state["paired"] = True
    save_state(state)

    return {
        "token": state["api_token"],
        "device_id": state["device_id"]
    }

@app.post("/api/control")
def control(data: dict, authorization: str = Header(None)):
    if not state["paired"]:
        raise HTTPException(403, "Device not paired")

    token = authorization.split(" ", 1)[1]

    if token != state["api_token"]:
        raise HTTPException(401, "Invalid token")

    temp = float(data["target_temperature"])

    if temp < -30 or temp > 20:
        raise HTTPException(400, "Temperature out of range")

    state["target_temperature"] = temp
    save_state(state)

    return {
        "ok": True,
        "target_temperature": temp
    }
