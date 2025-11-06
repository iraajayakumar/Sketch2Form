import serial
import time
import json
import threading
import asyncio
from fastapi import WebSocket
from app.processor import process_shape


class SerialListener:
    def __init__(self, port="COM3", baudrate=9600, loop=None):
        self.port = port
        self.baudrate = baudrate
        self.running = False
        self.clients = set()  # WebSocket clients
        self.thread = None
        self.loop = loop or asyncio.get_event_loop()  # ✅ store FastAPI’s main event loop
        self.last_shape_time = 0  # ✅ Track last END_SHAPE time

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._read_serial, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False

    # async def register_client(self, websocket: WebSocket):
    #     await websocket.accept()
    #     self.clients.add(websocket)
    #     print("[SerialListener] WebSocket client connected")

    # def unregister_client(self, websocket: WebSocket):
    #     self.clients.discard(websocket)

    async def _broadcast(self, message: dict):
        """Broadcast JSON message to all WebSocket clients."""
        to_remove = []
        for ws in list(self.clients):
            try:
                await ws.send_json(message)
            except Exception:
                to_remove.append(ws)
        for ws in to_remove:
            self.clients.remove(ws)

    def _read_serial(self):
        """Read and process lines from the serial port."""
        buffer = []
        last_line = None

        try:
            with serial.Serial(self.port, self.baudrate, timeout=1) as ser:
                print(f"[SerialListener] ✅ Connected to {self.port}")

                while self.running:
                    line = ser.readline().decode(errors="ignore").strip()
                    if not line:
                        continue

                    print(f"[SerialListener] RAW: {line}")

                    if line == "START_SHAPE":
                        buffer = []
                        print("[SerialListener] 🟢 START_SHAPE detected")
                        
                    elif line == "END_SHAPE":
                        now = time.time()
                        if now - self.last_shape_time < 1.0:
                            continue
                        self.last_shape_time = now

                        if buffer:
                            print(f"[SerialListener] 🔵 END_SHAPE received — {len(buffer)} points collected")
                            # ✅ Always use the main FastAPI loop
                            asyncio.run_coroutine_threadsafe(process_shape(buffer), self.loop)
                            buffer = []


                    elif line == "CLEARED":
                        print("[SerialListener] 🧹 CLEARED signal received")
                        asyncio.run_coroutine_threadsafe(self._broadcast({"type": "clear"}), self.loop)

                    else:
                        try:
                            point = json.loads(line)
                            buffer.append(point)
                            print(f"[SerialListener] ➕ Point: {point}")
                        except json.JSONDecodeError:
                            print(f"[SerialListener] ⚠️ Skipped invalid JSON: {line}")

        except serial.SerialException as e:
            print(f"[SerialListener] Serial error: {e}")
        except Exception as e:
            print(f"[SerialListener] Error: {e}")
