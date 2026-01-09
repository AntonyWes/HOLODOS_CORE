from fastapi import FastAPI, HTTPException, Header
from state.state import generate_token, save_state, load_state

app = FastAPI()
STATE = load_state()

@app.get("/api/status")
def status():
    return {
        "paired": STATE["paired"],
        "device_id": STATE["device_id"],
        "target_temperature": STATE.get("target_temperature")
    }

@app.post("/api/pair")
def pair(data: dict):
    if STATE["paired"]:
        raise HTTPException(400, "Already paired")

    if data.get("pin") != STATE["pin"]:
        raise HTTPException(401, "Invalid PIN")

    STATE["api_token"] = generate_token()
    STATE["paired"] = True
    save_state(STATE)

    return {
        "token": STATE["api_token"],
        "device_id": STATE["device_id"]
    }

@app.post("/api/control")
def control(data: dict, authorization: str = Header(None)):
    if not STATE["paired"]:
        raise HTTPException(403, "Device not paired")

    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing or invalid Authorization header")

    token = authorization.split(" ", 1)[1]

    if token != STATE.get("api_token"):
        raise HTTPException(401, "Invalid token")

    if "target_temperature" not in data:
        raise HTTPException(400, "Missing target_temperature")

    temp = float(data["target_temperature"])
    if temp < -30 or temp > 20:
        raise HTTPException(400, "Temperature out of range")

    STATE["target_temperature"] = temp
    save_state(STATE)

    return {
        "ok": True,
        "target_temperature": temp
    }
