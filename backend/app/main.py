from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from app.serial_listener import SerialListener
from app.utils.broadcast import clients  # shared clients list

app = FastAPI(title="Sketch2Form Backend")

# ✅ Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

listener = None  # will be initialized on startup


@app.on_event("startup")
async def startup_event():
    global listener
    loop = asyncio.get_running_loop()  # ✅ get the active FastAPI loop
    listener = SerialListener(port="COM3", baudrate=9600, loop=loop)
    listener.start()
    print("[Backend] 🚀 Serial listener started.")


@app.on_event("shutdown")
async def shutdown_event():
    if listener:
        listener.stop()
        print("[Backend] 🛑 Serial listener stopped.")


@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Sketch2Form backend is running"}


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    clients.append(ws)
    print(f"[WebSocket] ✅ Client connected. Total clients: {len(clients)}")
    
    try:
        while True:
            # Keep connection alive by receiving messages
            await ws.receive_text()
    except WebSocketDisconnect:
        clients.remove(ws)
        print(f"[WebSocket] ❌ Client disconnected. Total clients: {len(clients)}")