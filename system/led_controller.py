import asyncio
from bleak import BleakClient

LED_BADGE_ADDRESS = "00:00:00:00:00:00" 
CHARACTERISTIC_UUID = "0000fee1-0000-1000-8000-00805f9b34fb"

async def send_to_led(text):
    async with BleakClient(LED_BADGE_ADDRESS) as client:
        payload = bytearray([0x00, 0x01]) + text.encode('utf-8')
        await client.write_gatt_char(CHARACTERISTIC_UUID, payload)

def update_led(line, direction):
    text = f"{line} {direction}"
    try:
        asyncio.run(send_to_led(text))
    except Exception as e:
        print(f"LED BT Error: {e}")
