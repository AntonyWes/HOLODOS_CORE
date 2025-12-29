
import qrcode
import uvicorn

class HOLODOS_API:
    def __init__(self, STATE: dict):
        if not STATE["paired"]:
            pair_url = f"http://localhost:8080/pair?pin={STATE['pin']}"
            img = qrcode.make(pair_url)
            img.save("pair_qr.png")
        
        uvicorn.run("api.app:app", host="0.0.0.0", port=8080)

            
        
        