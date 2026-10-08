// Real vendored WASM computation under Node; this is not browser UI validation.
import assert from 'node:assert/strict';
import { readFile, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import * as ort from '../web/assets/vendor/ort.wasm.min.mjs';
import { prepareImage, restoreProbability, findRegions } from '../web/try/processing.mjs';
const root = new URL('../', import.meta.url);
const bytes = async p => new Uint8Array(await readFile(new URL(p, root)));
const floats = async p => { const a = await bytes(p); return new Float32Array(a.buffer, a.byteOffset, a.byteLength / 4); };
const meta = JSON.parse(await readFile(new URL('validation/reference.json', root), 'utf8'));
ort.env.wasm.numThreads = 1;
ort.env.wasm.wasmPaths = new URL('web/assets/vendor/', root).href;
const session = await ort.InferenceSession.create(await bytes('web/assets/polyp.onnx'), { executionProviders: ['wasm'] });
const input = await floats('validation/reference-input.f32');
const reference = await floats('validation/reference-output.f32');
const tensor = new ort.Tensor('float32', input, [1, 3, 160, 160]);
const output = await session.run({ image: tensor });
const error = Math.max(...output.probability.data.map((v, i) => Math.abs(v - reference[i])));
assert(error < 0.0001, `WASM/PyTorch difference ${error}`);
output.probability.dispose(); tensor.dispose();
const prepared = prepareImage(await bytes('validation/reference-rgba.u8'), meta.width, meta.height);
const next = new ort.Tensor('float32', prepared.tensor, [1, 3, 160, 160]);
const result = await session.run({ image: next });
assert(result.probability.data.every(Number.isFinite));
const probability = restoreProbability(result.probability.data, meta.width, meta.height, prepared.box);
const checks = [];
for (const [threshold, expected] of [[0.4, 4], [0.85, 1], [0.2, 3]]) {
  const { mask, regions } = findRegions(probability, meta.width, meta.height, threshold);
  assert.equal(regions.length, expected);
  assert.equal(mask.length, meta.width * meta.height);
  assert.equal(mask.reduce((a, b) => a + b, 0), regions.reduce((a, r) => a + r.area_pixels, 0));
  for (const r of regions) {
    const [x, y, x2, y2] = r.bbox_xyxy;
    assert(x >= 0 && y >= 0 && x2 > x && y2 > y && x2 <= meta.width && y2 <= meta.height);
    assert(Number.isFinite(r.mean_model_score));
  }
  checks.push({ threshold, count: regions.length, selected_pixels: mask.reduce((a, b) => a + b, 0) });
}
assert.equal(findRegions(new Float32Array(100), 10, 10, 0.4).regions.length, 0);
const diagonal = new Float32Array(25); for (let i = 0; i < 5; i++) diagonal[i * 6] = 1;
assert.deepEqual(findRegions(diagonal, 5, 5, 0.4, 5).regions[0].bbox_xyxy, [0, 0, 5, 5]);
assert.equal(findRegions(diagonal, 5, 5, 0.4, 6).regions.length, 0);
const report = { engine: 'ONNX Runtime Web WASM under Node', node: process.version, max_absolute_probability_error: error, thresholds: checks, browser_ui_tested: false };
await writeFile(new URL('validation/browser-results.json', root), JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify(report, null, 2));
result.probability.dispose(); next.dispose(); await session.release();
