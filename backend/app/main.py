from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from app.serial_listener import SerialListener
import asyncio

app = FastAPI(title="Sketch2Form Backend")

# store connected websocket clients
clients = []

# create the serial listener instance
listener = SerialListener(port="COM3", baudrate=9600)

@app.on_event("startup")
async def startup_event():
    """Start the serial listener when FastAPI starts."""
    listener.start()
    print("[Backend] Serial listener started.")
    
@app.on_event("shutdown")
async def shutdown_event():
    """Stop the serial listener when FastAPI shuts down."""
    listener.stop()
    print("[Backend] Serial listener stopped.")

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Sketch2Form backend is running"}

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    clients.append(ws)
    print("Client connected. Total clients:", len(clients))
    try:
        while True:
            # Keep alive / receive messages from frontend if needed
            data = await ws.receive_text()
            print("Received from client:", data)
    except WebSocketDisconnect:
        clients.remove(ws)
        listener.unregister_client(ws)
        print("Client disconnected. Total clients:", len(clients))


# helper: broadcast to all clients
async def broadcast_message(message: str):
    """Send message to all connected clients"""
    to_remove = []
    for client in clients:
        try:
            await client.send_text(message)
        except:
            to_remove.append(client)
    for r in to_remove:
        clients.remove(r)
