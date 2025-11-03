import serial
import json
import threading
import time
from fastapi import WebSocket

class SerialListener:
    def __init__(self, port="COM3", baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.running = False
        self.clients = set()  # WebSocket clients
        self.thread = None

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._read_serial, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False

    async def register_client(self, websocket: WebSocket):
        await websocket.accept()
        self.clients.add(websocket)

    def unregister_client(self, websocket: WebSocket):
        self.clients.discard(websocket)

    async def _broadcast(self, message: dict):
        # Send the data to all connected websocket clients
        to_remove = []
        for ws in list(self.clients):
            try:
                await ws.send_json(message)
            except Exception:
                to_remove.append(ws)
        for ws in to_remove:
            self.clients.remove(ws)

    def _read_serial(self):
        buffer = []
        last_line = None  # Track the last serial line

        try:
            with serial.Serial(self.port, self.baudrate, timeout=1) as ser:
                print(f"[SerialListener] Connected to {self.port}")
                while self.running:
                    line = ser.readline().decode(errors="ignore").strip()

                    if not line:
                        continue
                    
                    # Show every raw serial line
                    print(f"[SerialListener] RAW: {line}")

                    # --- Ignore duplicate END_SHAPE lines ---
                    if line == "END_SHAPE" and last_line == "END_SHAPE":
                        continue
                    last_line = line
                    # ---------------------------------------

                    if line == "START_SHAPE":
                        buffer = []
                        print("[SerialListener] 🟢 START_SHAPE detected")
                        

                    elif line == "END_SHAPE":
                        if buffer:
                            print(f"[SerialListener] 🔵 END_SHAPE received — {len(buffer)} points collected")
                            import asyncio
                            asyncio.run(self._broadcast({
                                "type": "shape",
                                "points": buffer
                            }))
                            buffer = []

                    elif line == "CLEARED":
                        print("[SerialListener] 🧹 CLEARED signal received")
                        import asyncio
                        asyncio.run(self._broadcast({"type": "clear"}))

                    else:
                        try:
                            point = json.loads(line)
                            buffer.append(point)
                            print(f"[SerialListener] ➕ Point: {point}")
                        except json.JSONDecodeError:
                            print(f"[SerialListener] ⚠️ Skipped invalid JSON: {line}")
                            pass

        except serial.SerialException as e:
            print(f"[SerialListener] Serial error: {e}")
        except Exception as e:
            print(f"[SerialListener] Error: {e}")
