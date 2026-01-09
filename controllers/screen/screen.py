import spidev
import RPi.GPIO as GPIO
import time
import io
import re
import cairosvg
from PIL import Image, ImageDraw, ImageFont


class DisplayDriver:
    def __init__(self, dc=9, rst=25, bus=0, device=0):
        self.dc = dc
        self.rst = rst
        self.width = 320
        self.height = 240
        
        self.spi = spidev.SpiDev()
        self.spi.open(bus, device)
        self.spi.max_speed_hz = 64000000
        self.spi.mode = 0b00
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.dc, GPIO.OUT)
        GPIO.setup(self.rst, GPIO.OUT)
        
        self.init_display()

    def write_cmd(self, cmd):
        GPIO.output(self.dc, 0)
        self.spi.xfer([cmd])

    def write_data(self, data):
        GPIO.output(self.dc, 1)
        if isinstance(data, int):
            self.spi.xfer([data])
        else:
            for i in range(0, len(data), 4096):
                self.spi.xfer(data[i:i+4096])

    def reset(self):
        GPIO.output(self.rst, 0)
        time.sleep(0.1)
        GPIO.output(self.rst, 1)
        time.sleep(0.1)

    def init_display(self):
        self.reset()
        commands = [
            (0x01, None),
            (0x11, None),
            (0x3A, [0x55]),

            (0x36, [0x60]),        
            
            (0x21, None),
            
            (0x13, None),
            (0x29, None),
        ]
        for cmd, data in commands:
            self.write_cmd(cmd)
            if data: self.write_data(data)
            time.sleep(0.1)

    def show(self, image):
        img = image.resize((self.width, self.height)).convert("RGB")
        self.write_cmd(0x2A)
        self.write_data([0, 0, (self.width-1)>>8, (self.width-1)&0xFF])
        self.write_cmd(0x2B)
        self.write_data([0, 0, (self.height-1)>>8, (self.height-1)&0xFF])
        self.write_cmd(0x2C)
        
        pix = list(img.getdata())
        out = bytearray(len(pix) * 2)
        
        for i, (r, g, b) in enumerate(pix):
            color = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
            out[i*2] = (color >> 8) & 0xFF
            out[i*2 + 1] = color & 0xFF
            
        self.write_data(list(out))

def render(temp, humidity, target, is_cooling, is_open, wifi_connected=True):
    W, H = 320, 240
    LEFT_W = 210
    
    img = Image.new("RGB", (W, H), (0, 0, 0))
    draw = ImageDraw.Draw(img)

    try:
        font_huge = ImageFont.truetype("DejaVuSans-Bold.ttf", 90)
        font_time = ImageFont.truetype("DejaVuSans-Bold.ttf", 26)
        font_med = ImageFont.truetype("DejaVuSans.ttf", 16)
        font_label = ImageFont.truetype("DejaVuSans-Bold.ttf", 10)
    except:
        font_huge = font_time = font_med = font_label = ImageFont.load_default()

    def draw_svg(canvas, svg_path, position, size=(24, 24), color=(255, 255, 255)):
        try:
            with open(svg_path, 'r') as f:
                svg_content = f.read()
            
            hex_color = '#%02x%02x%02x' % color
            
            svg_content = re.sub(r'stroke="[^"]+"', f'stroke="{hex_color}"', svg_content)
            svg_content = svg_content.replace('currentColor', hex_color)

            png_data = cairosvg.svg2png(
                bytestring=svg_content.encode('utf-8'),
                output_width=size[0],
                output_height=size[1]
            )
            
            icon_img = Image.open(io.BytesIO(png_data)).convert("RGBA")
            canvas.paste(icon_img, position, icon_img)
        except Exception as e:
            print(f"Error drawing {svg_path}: {e}")

    draw.rectangle([0, 0, LEFT_W, H], fill=(10, 10, 10))
    for x in range(0, LEFT_W, 12):
        for y in range(0, H, 12):
            draw.point((x, y), fill=(40, 40, 40))

    wifi_color = (82, 82, 82) if wifi_connected else (239, 68, 68)
    draw_svg(img, "wifi.svg" if wifi_connected else "wifi-off.svg", (12, 12), (18, 18), wifi_color)

    temp_color = (239, 68, 68) if is_open else (244, 244, 245)
    draw.text((20, 55), f"{temp:.1f}", font=font_huge, fill=temp_color)
    draw.text((182, 65), "°", font=font_time, fill=(82, 82, 82))

    draw.line([0, 195, LEFT_W, 195], fill=(30, 30, 30))
    draw.line([LEFT_W//2, 195, LEFT_W//2, 240], fill=(30, 30, 30))
    
    draw_svg(img, "target.svg", (15, 208), (16, 16), (82, 82, 82))
    draw.text((38, 202), "SET", font=font_label, fill=(82, 82, 82))
    draw.text((38, 215), f"{target:.1f}°", font=font_med, fill=(161, 161, 170))
    
    draw_svg(img, "droplets.svg", (120, 208), (16, 16), (82, 82, 82))
    draw.text((143, 202), "HUM", font=font_label, fill=(82, 82, 82))
    draw.text((143, 215), f"{humidity}%", font=font_med, fill=(161, 161, 170))

    draw.rectangle([LEFT_W, 0, W, 55], fill=(15, 15, 15))
    draw.text((235, 12), time.strftime("%H:%M"), font=font_time, fill=(212, 212, 216))

    cool_bg = (8, 47, 73) if is_cooling else (0, 0, 0)
    cool_text = (34, 211, 238) if is_cooling else (63, 63, 70)
    draw.rectangle([LEFT_W, 55, W, 147], fill=cool_bg)
    draw_svg(img, "snowflake.svg", (253, 75), (24, 24), cool_text)
    draw.text((245, 110), "ACTIVE" if is_cooling else "IDLE", font=font_label, fill=cool_text)

    door_bg = (220, 38, 38) if is_open else (24, 24, 27)
    door_text = (255, 255, 255) if is_open else (63, 63, 70)
    draw.rectangle([LEFT_W, 147, W, H], fill=door_bg)
    draw_svg(img, "lock-open.svg" if is_open else "lock.svg", (253, 165), (24, 24), door_text)
    draw.text((245, 205), "OPEN" if is_open else "LOCK", font=font_label, fill=door_text)

    return img


# try:
     
    
#     image = render_holodos_screen(4.2, 42, 4.0, False, True)
#     display.show(image)
#     time.sleep(5)
#     image = render_holodos_screen(4.2, 42, 4.0, True, False, False)
#     display.show(image)


# finally:
#     GPIO.cleanup()
