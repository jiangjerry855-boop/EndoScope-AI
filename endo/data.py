import hashlib
import json
from pathlib import Path
import numpy as np
from PIL import Image, ImageOps
import torch
from torch.utils.data import Dataset


def load_rgb(path):
    with Image.open(path) as im:
        if im.width * im.height > 20_000_000:
            raise ValueError("Image exceeds 20 megapixels. Resize before inference.")
        return ImageOps.exif_transpose(im).convert("RGB")


def letterbox(image, size, mask=False):
    """Keep aspect ratio; return (padded image, x/y/width/height of content)."""
    w, h = image.size
    scale = min(size / w, size / h)
    nw, nh = max(1, round(w * scale)), max(1, round(h * scale))
    resized = image.resize((nw, nh), Image.Resampling.NEAREST if mask else Image.Resampling.BILINEAR)
    canvas = Image.new("L" if mask else "RGB", (size, size))
    x, y = (size - nw) // 2, (size - nh) // 2
    canvas.paste(resized, (x, y))
    return canvas, (x, y, nw, nh)


def image_tensor(image, size):
    box, meta = letterbox(image, size)
    x = np.asarray(box, dtype=np.float32).transpose(2, 0, 1) / 255.0
    return torch.from_numpy(x.copy()), meta


class PolypDataset(Dataset):
    """Preload resized inputs; pad is excluded from the training loss."""
    def __init__(self, root, split, size=160, augment=False):
        self.root = Path(root)
        manifest = json.loads((self.root / "manifest.json").read_text())
        self.rows = [r for r in manifest["samples"] if r["split"] == split]
        if not self.rows:
            raise ValueError(f"No samples for split: {split}")
        self.augment, self.samples, self.areas = augment, [], []
        for row in self.rows:
            image = load_rgb(self.root / row["image"])
            with Image.open(self.root / row["mask"]) as im:
                a = np.asarray(im.convert("L"))
            mask = Image.fromarray(((a > 0) * 255).astype(np.uint8))
            if image.size != mask.size:
                raise ValueError(f"Image/mask size mismatch: {row['id']}")
            tx, (x, y, w, h) = image_tensor(image, size)
            tm, _ = letterbox(mask, size, mask=True)
            ty = torch.from_numpy((np.asarray(tm) > 127).astype(np.float32).copy())[None]
            valid = torch.zeros_like(ty)
            valid[:, y:y+h, x:x+w] = 1
            self.samples.append((tx, ty, valid))
            self.areas.append(float((a > 0).mean()))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        x, y, valid = (v.clone() for v in self.samples[idx])
        if self.augment:
            k = int(torch.randint(4, (1,)).item())
            x, y, valid = [torch.rot90(v, k, (1, 2)) for v in (x, y, valid)]
            if torch.rand(()) < 0.5:
                x, y, valid = [v.flip(2) for v in (x, y, valid)]
            gain = float(torch.empty(()).uniform_(0.85, 1.15))
            x = (x * gain).clamp(0, 1)
        return x, y, valid


def validate_manifest(root):
    root = Path(root)
    data = json.loads((root / "manifest.json").read_text())
    seen_ids, seen_hashes, counts = set(), set(), {}
    for row in data["samples"]:
        if row["split"] not in {"train", "val", "test"}:
            raise ValueError("Unknown split")
        if row["id"] in seen_ids:
            raise ValueError("Duplicate sample ID across dataset")
        seen_ids.add(row["id"])
        digest = hashlib.sha256(load_rgb(root / row["image"]).tobytes()).hexdigest()
        if digest in seen_hashes:
            raise ValueError("Exact duplicate decoded image across dataset")
        seen_hashes.add(digest)
        with Image.open(root / row["mask"]) as im:
            values = set(np.unique(np.asarray(im)).tolist())
        if not values.issubset({0, 255}):
            raise ValueError("Masks must be binary 0/255 PNGs")
        counts[row["split"]] = counts.get(row["split"], 0) + 1
    return counts
