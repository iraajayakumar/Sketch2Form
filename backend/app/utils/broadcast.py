# app/utils/broadcast.py

clients = []

async def broadcast_message(message: str):
    """Send message to all connected WebSocket clients."""
    to_remove = []
    for client in clients:
        try:
            await client.send_text(message)
        except Exception:
            to_remove.append(client)
    for r in to_remove:
        clients.remove(r)
