import asyncio
from bleak import BleakClient, BleakScanner

SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
RX_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"  # Write to ESP32
TX_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"  # Notify from ESP32
class STQV1:
    def __init__(self, name="STQV1"):
        self.name = name
        self.client = None
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(self.connect())

    async def connect(self):
        print("Scanning for devices...")
        device = await BleakScanner.find_device_by_filter(
            lambda d, ad: d.name == self.name
        )
        if not device:
            raise Exception(f"Could not find {self.name}")
        self.client = BleakClient(device)
        await self.client.connect()
        print(f"Connected to {self.name}")

    async def _send(self, cmd):
        if not self.client or not self.client.is_connected:
            raise Exception("Not connected to STQV1")
        await self.client.write_gatt_char(RX_UUID, cmd.encode())

    def send(self, cmd):
        self.loop.run_until_complete(self._send(cmd))

    # Commands
    def walk(self):
        self.send("walk()")

    def writeScreen(self, text):
        self.send(f'writeScreen("{text}")')

    def writeMotor(self, val):
        self.send(f"writeMotor({val})")

    def reset(self):
        self.send("reset()")

    def close(self):
        if self.client:
            self.loop.run_until_complete(self.client.disconnect())
