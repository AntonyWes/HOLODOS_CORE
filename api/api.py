import qrcode
from pathlib import Path

class HOLODOS_API:
    def __init__(self, state: dict):
        self.state = state

    def prepare_pairing(self):
        if self.state["paired"]:
            return

        img = qrcode.make(self.state["pin"])
        Path("pair_qr.png").unlink(missing_ok=True)
        img.save("pair_qr.png")

    def print_info(self):
        print("=== HOLODOS ===")
        print(f"Device ID: {self.state['device_id']}")
        print(f"PIN: {self.state['pin']}")
        print("QR code saved as pair_qr.png")
