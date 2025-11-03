from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import asyncio

app = FastAPI(title="ShapeVision Backend")

# store connected websocket clients
clients = []

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
            # (Optional) if frontend sends any messages
            data = await ws.receive_text()
            print("Received from client:", data)
    except WebSocketDisconnect:
        clients.remove(ws)
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
