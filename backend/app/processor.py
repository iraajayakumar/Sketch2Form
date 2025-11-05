import json
import os
import asyncio
from datetime import datetime
import numpy as np

# ✅ Import both process_shape and predict_shape from ml.py
from app.ml.ml import process_shape as ml_process_shape, predict_shape
from app.utils.broadcast import broadcast_message  # if not imported, keep your existing async broadcast function

SAVE_DIR = "shapes"
os.makedirs(SAVE_DIR, exist_ok=True)


def normalize_points(points):
    xs = [p["x"] for p in points]
    ys = [p["y"] for p in points]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    width = max_x - min_x or 1
    height = max_y - min_y or 1

    norm = [{"x": (p["x"] - min_x) / width,
             "y": (p["y"] - min_y) / height,
             "t": p.get("t", 0)} for p in points]
    return norm


async def process_shape(points):
    """Process incoming shape data from Arduino."""
    if not points:
        return

    # Step 1: Normalize
    norm_points = normalize_points(points)

    # Step 2: Predict shape using ML model
    label, confidence = predict_shape(norm_points)

    # Step 3: Save locally
    shape_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_path = os.path.join(SAVE_DIR, f"shape_{shape_id}.json")
    with open(save_path, "w") as f:
        json.dump({
            "points": points,
            "label": label,
            "confidence": confidence
        }, f, indent=2)

    # Step 4: Broadcast result
    await broadcast_message(json.dumps({
        "type": "shape_result",
        "label": label,
        "confidence": confidence,
        "points": norm_points
    }))

    print(f"[Processor] ✅ Shape saved as {label} ({confidence:.2f})")


