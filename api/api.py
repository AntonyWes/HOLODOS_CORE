
import qrcode
import uvicorn

class HOLODOS_API:
    def __init__(self, STATE: dict):
        if not STATE["paired"]:
            img = qrcode.make(STATE['pin'])
            img.save("pair_qr.png")
        print(f"Device ID: {STATE['device_id']}")
        print(f"PIN: {STATE['pin']}")
        print("QR code saved as pair_qr.png")
        uvicorn.run("api.app:app", host="0.0.0.0", port=8080)

            
        
        