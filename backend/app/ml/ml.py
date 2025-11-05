import os
import json
import time
import numpy as np
import asyncio
from datetime import datetime
from collections import Counter
from app.utils.broadcast import broadcast_message
import tensorflow as tf  # for TFLite model inference

SAVE_DIR = "shapes"
os.makedirs(SAVE_DIR, exist_ok=True)

# === MODEL SETUP ===
MODEL_PATH = os.path.join("app", "ml", "shape_classifier.tflite")

# --- paste at top of ml.py where model is loaded (replace previous input_details usage) ---
interpreter = tf.lite.Interpreter(model_path=MODEL_PATH)
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

LABELS = ["square", "rectangle", "triangle", "circle"]

# print actual model input shape for debugging
print("[ML] TFLite input details:", input_details)
# input_details[0]['shape'] is often like [1, 64, 5] or [1, -1, 5] (if dynamic)
shape_expected = input_details[0].get("shape", None)
if shape_expected is None:
    # fallback
    seq_len = 64
    feat_dim = 5
else:
    # shape_expected likely [1, seq_len, feat_dim] (0:batch,1:seq,2:feat)
    # if some dimension is 0/1/-1, fallback to defaults
    seq_len = int(shape_expected[1]) if len(shape_expected) > 1 and shape_expected[1] > 0 else 64
    feat_dim = int(shape_expected[2]) if len(shape_expected) > 2 and shape_expected[2] > 0 else 5

print(f"[ML] Model expects seq_len={seq_len}, feat_dim={feat_dim}")

# --- helper functions for resampling and feature building ---
import math

def resample_along_length(xy, target_len):
    """
    xy: ndarray [L,2]
    returns ndarray [target_len,2] resampled along cumulative arc length.
    """
    if len(xy) == 0:
        return np.zeros((target_len, 2), dtype=np.float32)
    if len(xy) == 1:
        return np.repeat(xy, target_len, axis=0).astype(np.float32)

    diffs = np.diff(xy, axis=0)
    dists = np.linalg.norm(diffs, axis=1)
    cum = np.concatenate(([0.0], np.cumsum(dists)))
    total = cum[-1]
    if total == 0:
        return np.repeat(xy[:1], target_len, axis=0).astype(np.float32)

    t = np.linspace(0.0, total, target_len)
    x_interp = np.interp(t, cum, xy[:, 0])
    y_interp = np.interp(t, cum, xy[:, 1])
    return np.stack([x_interp, y_interp], axis=1).astype(np.float32)

def build_features_from_xyxy_t(xy, times=None):
    """
    Build 5-feature vector per point:
      [x_norm, y_norm, dx, dy, speed]
    xy: [L,2] already normalized to [0,1]
    times: list or array of timestamps for each point (optional, used for speed), if None, speed uses euclidean delta
    returns ndarray [L,5]
    """
    L = xy.shape[0]
    # compute deltas (prepend zero for first)
    d = np.vstack((np.zeros((1,2), dtype=np.float32), np.diff(xy, axis=0).astype(np.float32)))
    if times is not None and len(times) == L:
        dt = np.vstack((np.array([[0.0]]), np.diff(np.array(times).astype(np.float32).reshape(-1,1))))
        # avoid zero dt
        dt[dt==0] = 1.0
        speed = np.linalg.norm(d, axis=1, keepdims=True) / dt
    else:
        speed = np.linalg.norm(d, axis=1, keepdims=True)
    feats = np.concatenate([xy.astype(np.float32), d.astype(np.float32), speed.astype(np.float32)], axis=1)  # [L,5]
    return feats

# --- replacement normalize_points + predict_shape ---
def normalize_points(points, num_samples=64):
    """Normalize coordinates to [0,1] and resample to fixed length, matching model input shape (1, 64, 5)."""
    xs = np.array([p.get("x", 0) for p in points], dtype=np.float32)
    ys = np.array([p.get("y", 0) for p in points], dtype=np.float32)
    ts = np.array([p.get("t", 0) for p in points], dtype=np.float32)
    cs = np.array([p.get("c", 0) for p in points], dtype=np.float32)

    # Normalize x and y
    min_x, max_x = xs.min(), xs.max()
    min_y, max_y = ys.min(), ys.max()
    width, height = max_x - min_x or 1, max_y - min_y or 1
    xs = (xs - min_x) / width
    ys = (ys - min_y) / height

    # Normalize time to [0,1]
    ts = (ts - ts.min()) / (ts.max() - ts.min() + 1e-6)

    # Normalize color to [0,1] using max 16-bit RGB565 value
    cs = cs / 65535.0

    # Stack features: (x, y, t, c, pen_down=1)
    features = np.stack([xs, ys, ts, cs, np.ones_like(xs)], axis=1)

    # Resample to fixed number of points
    indices = np.linspace(0, len(features) - 1, num_samples).astype(int)
    resampled = features[indices]

    # Add batch dimension
    return resampled.reshape(1, num_samples, 5).astype(np.float32)


def predict_shape(points):
    """Run TFLite model inference (uses normalize_points above)."""
    # produce input matching model expected seq_len and feat_dim
    input_data = normalize_points(points, num_samples=seq_len)
    # debug print:
    # print("[ML] input_data.shape:", input_data.shape, " dtype:", input_data.dtype)
    interpreter.set_tensor(input_details[0]["index"], input_data)
    interpreter.invoke()
    output_data = interpreter.get_tensor(output_details[0]["index"])[0]
    pred_idx = int(np.argmax(output_data))
    confidence = float(np.max(output_data))
    label = LABELS[pred_idx] if pred_idx < len(LABELS) else "unknown"
    return label, confidence


# === MAIN SHAPE PROCESSOR ===
async def process_shape(points):
    """Process one completed shape batch from Arduino."""
    if not points:
        return

    # Step 1: Get dominant color
    colors = [p.get("c", 0) for p in points if "c" in p]
    if colors:
        color_value = Counter(colors).most_common(1)[0][0]
        color_hex = rgb565_to_hex(color_value)
    else:
        color_hex = "#FFFFFF"

    # Step 2: Predict shape and confidence
    print(f"[ML] 🔍 Received {len(points)} points for classification")
    label, confidence = predict_shape(points)

    # Step 3: Save results locally
    shape_data = {
        "timestamp": datetime.now().isoformat(),
        "label": label,
        "confidence": confidence,
        "color": color_hex,
        "points": points
    }
    filename = os.path.join(SAVE_DIR, f"shape_{int(time.time())}.json")
    with open(filename, "w") as f:
        json.dump(shape_data, f, indent=2)

    # Step 4: Broadcast to clients
    message = {
        "type": "shape_result",
        "label": label,
        "confidence": confidence,
        "color": color_hex
    }
    await broadcast_message(json.dumps(message))

    print(f"[ML] ✅ Shape predicted: {label} ({confidence:.2f}) | Color: {color_hex}")
