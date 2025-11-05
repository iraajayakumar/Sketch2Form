import os
import json
import numpy as np
from glob import glob

RAW_DATA_DIR = 'raw_data'
PROCESSED_DIR = 'processed'
LABELS = ['square', 'rectangle', 'triangle', 'circle']
SEQ_LEN = 64
FEAT_DIM = 5

os.makedirs(PROCESSED_DIR, exist_ok=True)

def normalize_and_resample(points, seq_len=SEQ_LEN):
    xs = np.array([p.get('x', 0) for p in points], dtype=np.float32)
    ys = np.array([p.get('y', 0) for p in points], dtype=np.float32)
    ts = np.array([p.get('t', 0) for p in points], dtype=np.float32)
    cs = np.array([p.get('c', 0) for p in points], dtype=np.float32)

    # Normalize
    min_x, max_x = xs.min(), xs.max()
    min_y, max_y = ys.min(), ys.max()
    xs = (xs - min_x) / (max_x - min_x if max_x-min_x > 0 else 1)
    ys = (ys - min_y) / (max_y - min_y if max_y-min_y > 0 else 1)
    ts = (ts - ts.min()) / (ts.max() - ts.min() + 1e-6)
    cs = cs / 65535.0
    pen_down = np.ones_like(xs)

    # Stack features
    features = np.stack([xs, ys, ts, cs, pen_down], axis=1)

    # Resample to fixed SEQ_LEN using interpolation
    idxs = np.linspace(0, len(features) - 1, seq_len).astype(np.int32)
    resampled = features[idxs]

    return resampled.astype(np.float32)

def process_all():
    files = glob(os.path.join(RAW_DATA_DIR, '*.json'))
    X = []
    y = []

    for f in files:
        with open(f, 'r') as fp:
            data = json.load(fp)
        label = data['label'].lower()
        if label not in LABELS:
            continue
        label_idx = LABELS.index(label)
        points = data['points']
        arr = normalize_and_resample(points)
        X.append(arr)
        y.append(label_idx)

    X = np.stack(X, axis=0) # shape (N, 64, 5)
    y = np.array(y, dtype=np.int64) # shape (N,)
    np.save(os.path.join(PROCESSED_DIR, 'shapes_X.npy'), X)
    np.save(os.path.join(PROCESSED_DIR, 'shapes_y.npy'), y)
    print(f'Dataset saved: {X.shape=} {y.shape=}')
    for idx, lbl in enumerate(LABELS):
        print(f'Class "{lbl}": {(y==idx).sum()} samples')

if __name__ == '__main__':
    process_all()
