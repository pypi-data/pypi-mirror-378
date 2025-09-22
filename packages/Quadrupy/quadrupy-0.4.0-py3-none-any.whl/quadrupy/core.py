import asyncio
import serial
import time

class STQV1:
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(self.connect())
        self.esp32 = serial.Serial("COM12", baudrate=115200, timeout=1)
        time.sleep(2)

    async def connect(self):
        print("Scanning for devices...")

    async def _send(self, cmd):
        self.esp32.write(b"{}".format(cmd))

    def send(self, cmd):
        self.loop.run_until_complete(self._send(cmd))

    def walk(self):
        self.send("walk()\n")

    def writeScreen(self, text):
        self.send(f'writeScreen("{text}")\n')

    def writeMotor(self, val):
        self.send(f"writeMotor({val})\n")

    def led(self, state):
        if (state):
            self.send("ON\n")
        else:
            self.send("OFF\N")

    def reset(self):
        self.send("reset()\n")

    def close(self):
        self.esp32.close()
