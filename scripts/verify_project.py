"""Check packaged assets, desktop inference/exports; prepare WASM test inputs."""
from pathlib import Path
from html.parser import HTMLParser
import hashlib, json, re, sys
import numpy as np
from PIL import Image
import PIL, scipy, torch
from serve_browser import ensure_runtime
ensure_runtime()
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from endo.inference import Predictor, export_prediction
from endo.data import image_tensor
WEB = ROOT / 'web'
OUT = ROOT / 'validation'
OUT.mkdir(exist_ok=True)

class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.ids = set(); self.refs = []
    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if 'id' in d:
            assert d['id'] not in self.ids, f'Duplicate ID {d["id"]}'
            self.ids.add(d['id'])
        self.refs += [d[k] for k in ('src', 'href', 'poster') if k in d]

for html, script in [('index.html', 'demo.js'), ('try/index.html', 'try/app.js')]:
    page = Page(); page.feed((WEB / html).read_text())
    for ref in page.refs:
        if ref.startswith('/'):
            target = WEB / ref.lstrip('/')
            if ref.endswith('/'): target /= 'index.html'
            assert target.is_file(), f'Missing asset {ref}'
    for target in re.findall(r"(?:querySelector\(|\$\()'\#([\w-]+)'\)", (WEB / script).read_text()):
        assert target in page.ids, f'Missing DOM target {target}'
info = json.loads((WEB / 'assets/model-info.json').read_text())
for path, key in [(ROOT / 'models/polyp_unet.pt', 'checkpoint_sha256'), (WEB / 'assets/polyp.onnx', 'onnx_sha256')]:
    assert hashlib.sha256(path.read_bytes()).hexdigest() == info[key], path
assert (ROOT / 'examples/01_polyp.jpg').read_bytes() == (WEB / 'assets/examples/01_polyp.jpg').read_bytes()
for name in ['ort.wasm.min.js', 'ort.wasm.min.mjs', 'ort-wasm-simd-threaded.mjs', 'ort-wasm-simd-threaded.wasm', 'ONNX-RUNTIME-LICENSE.txt']:
    assert (WEB / 'assets/vendor' / name).stat().st_size > 100
steps = json.loads((WEB / 'assets/chapters.json').read_text())
assert steps[0]['start'] == 0 and steps[-1]['end'] >= 32.666
assert all(a['end'] == b['start'] for a, b in zip(steps, steps[1:]))
for language in ('en', 'zh'):
    assert (WEB / f'assets/captions/{language}.vtt').read_text().count('-->') == len(steps)

predictor = Predictor(ROOT / 'models/polyp_unet.pt')
image = Image.open(ROOT / 'examples/01_polyp.jpg').convert('RGB')
checks = []
for threshold, expected_count in [(0.4, 4), (0.85, 1), (0.2, 3)]:
    result, mask, overlay = predictor.predict(image, threshold)
    assert len(result['regions']) == expected_count, (threshold, result)
    destination = OUT / f'desktop-{threshold:.2f}'
    export_prediction(destination, result, mask, overlay)
    exported = json.loads((destination / 'result.json').read_text())
    assert exported['threshold'] == threshold
    assert (exported['image_width'], exported['image_height']) == image.size
    for filename in ('mask.png', 'overlay.png'):
        assert Image.open(destination / filename).size == image.size
    assert set(np.unique(np.asarray(Image.open(destination / 'mask.png')))).issubset({0, 255})
    assert sum(r['area_pixels'] for r in result['regions']) == int(mask.sum())
    for region in result['regions']:
        x1, y1, x2, y2 = region['bbox_xyxy']
        assert 0 <= x1 < x2 <= image.width and 0 <= y1 < y2 <= image.height
        assert np.isfinite(region['mean_model_score'])
    checks.append({'threshold': threshold, 'count': expected_count, 'selected_pixels': int(mask.sum())})
input_tensor, box = image_tensor(image, 160)
with torch.inference_mode():
    reference = predictor.model(input_tensor[None]).sigmoid().numpy()
assert np.isfinite(reference).all()
input_tensor.numpy().tofile(OUT / 'reference-input.f32')
reference.tofile(OUT / 'reference-output.f32')
np.asarray(image.convert('RGBA')).tofile(OUT / 'reference-rgba.u8')
(OUT / 'reference.json').write_text(json.dumps({'width': image.width, 'height': image.height, 'letterbox': box}))
report = {'python': sys.version.split()[0], 'torch': torch.__version__, 'numpy': np.__version__, 'pillow': PIL.__version__, 'scipy': scipy.__version__, 'image_size': image.size, 'thresholds': checks, 'assets_and_hashes': 'passed', 'desktop_gui_tested': False}
(OUT / 'desktop-results.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
