from fastapi import FastAPI, HTTPException
from state.state import load_state, save_state, generate_token

app = FastAPI()
state = load_state()

@app.get("/api/status")
def status():
    return {
        "paired": state["paired"],
        "device_id": state["device_id"]
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
