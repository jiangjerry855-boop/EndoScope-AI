import hashlib
import json
import time
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage
import torch
from .data import image_tensor, load_rgb
from .model import CompactUNet


def regions_from_mask(mask, probability=None, min_area=16):
    """8-connected components; boxes use exclusive right/bottom coordinates."""
    labels, _ = ndimage.label(mask, structure=np.ones((3, 3), dtype=np.uint8))
    objects = ndimage.find_objects(labels)
    regions, clean = [], np.zeros(mask.shape, dtype=bool)
    for label_id, slices in enumerate(objects, 1):
        if slices is None:
            continue
        region = labels[slices] == label_id
        area = int(region.sum())
        if area < min_area:
            continue
        clean[slices] |= region
        ys, xs = slices
        score = float(probability[slices][region].mean()) if probability is not None else None
        regions.append({"class": "polyp_candidate", "bbox_xyxy": [xs.start, ys.start, xs.stop, ys.stop],
                        "area_pixels": area, "mean_model_score": score})
    regions.sort(key=lambda r: r["area_pixels"], reverse=True)
    return clean, regions


def make_overlay(image, mask, regions):
    arr = np.asarray(image).copy()
    arr[mask] = (arr[mask] * 0.60 + np.array([28, 221, 176]) * 0.40).astype(np.uint8)
    out = Image.fromarray(arr)
    draw = ImageDraw.Draw(out)
    line = max(2, round(min(image.size) / 200))
    for idx, region in enumerate(regions, 1):
        x1, y1, x2, y2 = region["bbox_xyxy"]
        draw.rectangle((x1, y1, x2 - 1, y2 - 1), outline="#21edbf", width=line)
        text = f"#{idx} POLYP CANDIDATE"
        draw.rectangle((x1, max(0, y1 - 17), min(image.width, x1 + 143), max(17, y1)), fill="#073d35")
        draw.text((x1 + 3, max(0, y1 - 16)), text, fill="white")
    return out


class Predictor:
    def __init__(self, checkpoint, device="cpu", threads=4):
        path = Path(checkpoint)
        if not path.is_file():
            raise FileNotFoundError("Model missing. Run train.py or select the bundled polyp_unet.pt.")
        torch.set_num_threads(threads)
        # Restricted tensor/primitive deserialization; do not load arbitrary pickled model objects.
        meta = torch.load(path, map_location="cpu", weights_only=True)
        if meta.get("architecture") != "CompactUNet" or not meta.get("trained") or meta.get("classes") != ["polyp"]:
            raise ValueError("This checkpoint is not a trained CompactUNet polyp model.")
        self.size = int(meta["input_size"])
        if not 32 <= self.size <= 1024 or int(meta["base"]) not in (4, 8, 12, 16, 24, 32, 48, 64):
            raise ValueError("Unsupported model dimensions")
        self.model = CompactUNet(int(meta["base"])).to(device)
        self.model.load_state_dict(meta["state_dict"], strict=True)
        self.model.eval(); self.device = device
        self.metadata = {k: v for k, v in meta.items() if k != "state_dict"}
        self.sha256 = hashlib.sha256(path.read_bytes()).hexdigest()

    @torch.inference_mode()
    def predict(self, image, threshold=0.5, min_area=16):
        if not 0 < threshold < 1 or min_area < 1:
            raise ValueError("threshold must be between 0 and 1; min_area must be positive")
        image = image.convert("RGB")
        if image.width * image.height > 20_000_000:
            raise ValueError("Image exceeds 20 megapixels. Resize before inference.")
        start = time.perf_counter()
        tensor, (x, y, w, h) = image_tensor(image, self.size)
        probability = self.model(tensor[None].to(self.device)).sigmoid()[0, 0].cpu().numpy()
        if not np.isfinite(probability).all():
            raise ValueError("Model produced non-finite scores. Check the model weights.")
        probability = probability[y:y+h, x:x+w]
        probability = np.asarray(Image.fromarray(probability).resize(image.size, Image.Resampling.BILINEAR))
        mask, regions = regions_from_mask(probability >= threshold, probability, min_area)
        elapsed = (time.perf_counter() - start) * 1000
        result = {"project": "EndoScope AI", "research_only": True, "supported_class": "polyp",
                  "model_sha256": self.sha256, "image_width": image.width, "image_height": image.height,
                  "threshold": threshold, "min_component_area_pixels": min_area,
                  "inference_ms_including_pre_and_postprocessing": elapsed,
                  "regions": regions,
                  "notice": "Research prototype; scores are uncalibrated model activations, not disease probabilities. No candidate does not establish a normal examination."}
        return result, mask, make_overlay(image, mask, regions)


def export_prediction(directory, result, mask, overlay):
    directory = Path(directory); directory.mkdir(parents=True, exist_ok=True)
    (directory / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    Image.fromarray(mask.astype(np.uint8) * 255).save(directory / "mask.png")
    overlay.save(directory / "overlay.png")


def predict_file(predictor, source, output, threshold=0.5, min_area=16):
    image = load_rgb(source)
    result, mask, overlay = predictor.predict(image, threshold, min_area)
    result["source_filename"] = Path(source).name
    export_prediction(output, result, mask, overlay)
    return result
