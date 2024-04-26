import network
import time
from machine import SoftI2C, Pin
from I2C_LCD import I2cLcd
import urequests as requests
import neopixel
import uasyncio as asyncio

ssid = 'TMNL-D2F311'
password = 'PX9KS5PYJQ345MRM'

# Connect to Wi-Fi
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(ssid, password)

while not wifi.isconnected():
    pass

i2c = SoftI2C(scl=Pin(14), sda=Pin(13))
devices = i2c.scan()

if len(devices) == 0:
    print("No I2C device!")
else:
    for device in devices:
        print("I2C addr: " + hex(device))
        lcd = I2cLcd(i2c, device, 2, 16)

bitcoin_api_url = 'https://api.coincap.io/v2/assets/bitcoin/'

def get_bitcoin_price():
    try:
        response = requests.get(bitcoin_api_url)
        if response.status_code == 200:
            data = response.json()
            price_usd = round(float(data['data']['priceUsd']), 4)
            return price_usd
        else:
            print("HTTP error:", response.status_code, response.text)
            return None
    except Exception as e:
        print("Error fetching Bitcoin price:", e)
        return None

async def display_bitcoin_price():
    try:
        while True:
            bitcoin_price = get_bitcoin_price()
            if bitcoin_price is not None:
                formatted_price = "{:.4f}".format(bitcoin_price)

                lcd.clear()
                lcd.move_to(0, 0)
                lcd.putstr("Bitcoin Price:")
                lcd.move_to(0, 1)
                lcd.putstr(formatted_price)
            else:
                lcd.clear()
                lcd.putstr("Error fetching price")

            await asyncio.sleep(10)  # Update every 30 seconds (adjust as needed)
    except Exception as e:
        print("Exception:", e)

async def lamp_animation():
    try:
        pin = Pin(2, Pin.OUT)
        np = neopixel.NeoPixel(pin, 8)

        brightness = 10
        colors = [
            [brightness, brightness, 0],
            [brightness, brightness, brightness],
            
        ]

        while True:
            for i in range(0, 2):
                for j in range(0, 8):
                    np[j] = colors[i]
                    np.write()
                    await asyncio.sleep_ms(100)

    except Exception as e:
        print("Exception:", e)

# Run both tasks concurrently
try:
    loop = asyncio.get_event_loop()
    loop.create_task(display_bitcoin_price())
    loop.create_task(lamp_animation())
    loop.run_forever()
except KeyboardInterrupt:
    pass




