// State regression checks with DOM/worker doubles, not a browser rendering test.
import vm from 'node:vm';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
const elements = new Map(), requests = [], workers = [], downloads = [], timers = new Map(), blobs = new Map();
let timerId = 0, urlId = 0;
class Element {
  constructor(tag = 'div') { this.tag = tag; this.listeners = {}; this.children = []; this.disabled = false; this.width = 10; this.height = 10; this.files = []; this.value = ''; this.classList = { toggle() {}, add() {}, remove() {} }; }
  addEventListener(name, fn) { (this.listeners[name] ??= []).push(fn); }
  emit(name, event = {}) { for (const fn of this.listeners[name] ?? []) fn(event); }
  click() { if (this.tag === 'a' && this.download) downloads.push(this.download); this.emit('click'); }
  append(...items) { this.children.push(...items); }
  replaceChildren(...items) { this.children = items; }
  setAttribute() {}
  getContext() { return { clearRect() {}, fillRect() {}, drawImage() {}, putImageData() {}, strokeRect() {}, fillText() {}, measureText() { return { width: 20 }; }, getImageData: () => ({ data: new Uint8ClampedArray(this.width * this.height * 4) }), createImageData: (w, h) => ({ data: new Uint8ClampedArray(w * h * 4) }) }; }
  toBlob(callback) { callback(new Blob(['png'])); }
}
const get = selector => { if (!elements.has(selector)) elements.set(selector, new Element()); return elements.get(selector); };
get('#threshold').value = '0.40';
const document = {
  querySelector: s => s === '.sample' ? get('#samples').children[0] : get(s),
  querySelectorAll: s => s === '.sample' ? get('#samples').children : [],
  createElement: tag => new Element(tag)
};
const context = vm.createContext({
  document, Blob, Uint8Array, Uint8ClampedArray, Number, Math,
  ImageData: class { constructor(data, width, height) { Object.assign(this, { data, width, height }); } },
  Image: class { naturalWidth = 10; naturalHeight = 10; async decode() { if (blobs.get(this.src)?.bad) throw Error('bad image'); } },
  URL: { createObjectURL(blob) { const url = 'blob:' + ++urlId; blobs.set(url, blob); return url; }, revokeObjectURL(url) { blobs.delete(url); } },
  fetch: url => new Promise((resolve, reject) => requests.push({ url, resolve, reject })),
  Worker: class { constructor() { workers.push(this); this.messages = []; } postMessage(message) { this.messages.push(message); } terminate() { this.terminated = true; } },
  setTimeout: fn => { timers.set(++timerId, fn); return timerId; }, clearTimeout: id => timers.delete(id)
});
vm.runInContext(await readFile(new URL('../web/try/app.js', import.meta.url), 'utf8'), context);
const evaluate = code => vm.runInContext(code, context);
const settle = async () => { for (let i = 0; i < 8; i++) await Promise.resolve(); };
const loadResponse = request => request.resolve({ ok: true, blob: async () => ({ size: 100 }) });
const flush = () => { const pending = [...timers.values()]; timers.clear(); for (const fn of pending) fn(); };
const reply = (id, threshold = 0.4, regions = []) => workers.at(-1).onmessage({ data: { id, type: 'result', mask: new Uint8Array(100).buffer, regions, threshold, width: 10, height: 10, metadata: { checkpoint_sha256: 'test', onnx_sha256: 'test' }, metrics: { model_inference_ms: 1 } } });
// An older sample fetch must not replace the most recent selection.
get('#samples').children[1].click();
assert.equal(requests.length, 2);
loadResponse(requests[1]); await settle();
assert.equal(evaluate('imageName'), '02_sessile_polyp.jpg');
loadResponse(requests[0]); await settle();
assert.equal(evaluate('imageName'), '02_sessile_polyp.jpg');
// Inference produces a current result, including valid empty predictions.
get('#run').click();
let id = evaluate('requestId'); reply(id);
assert.equal(get('#export-json').disabled, false);
assert.match(get('#regions').innerHTML, /does not rule out/);
// Threshold changes immediately invalidate exports, even during debounce.
get('#threshold').value = '0.85'; get('#threshold').emit('input');
assert.equal(get('#export-json').disabled, true);
get('#export-json').click(); get('#export-overlay').click(); get('#export-mask').click();
assert.equal(downloads.length, 0);
const oldThresholdId = evaluate('requestId');
flush();
get('#threshold').value = '0.20'; get('#threshold').emit('input'); flush();
reply(oldThresholdId, 0.85);
assert.equal(get('#threshold').value, '0.20');
assert.equal(get('#export-json').disabled, true);
id = evaluate('requestId'); reply(id, 0.2);
assert.equal(get('#export-json').disabled, false);
get('#export-json').click(); assert.equal(downloads.length, 1);
// Selecting another image clears its predecessor and rejects a late worker result.
get('#samples').children[2].click();
reply(id, 0.2);
assert.equal(evaluate('lastResult'), null);
assert.equal(get('#export-json').disabled, true);
requests[2].reject(Error('offline')); await settle();
assert.equal(evaluate('imageData'), null);
assert.match(get('#status').textContent, /could not be loaded/);
// Bad input cannot resurrect a stale image or enable Run.
get('#file-input').files = [{ size: 100, name: 'broken.jpg', bad: true }]; get('#file-input').emit('change'); await settle();
assert.equal(get('#run').disabled, true);
assert.match(get('#status').textContent, /Could not open/);
get('#file-input').files = [{ size: 21 * 1024 * 1024, name: 'large.jpg' }]; get('#file-input').emit('change'); await settle();
assert.match(get('#status').textContent, /smaller than 20 MB/);
// Engine failure clears the result and leaves a retry path.
get('#file-input').files = [{ size: 100, name: 'valid.jpg' }]; get('#file-input').emit('change'); await settle();
get('#run').click();
workers.at(-1).onerror();
assert.equal(evaluate('worker'), null);
assert.equal(evaluate('lastResult'), null);
assert.equal(get('#run').disabled, false);
assert.equal(get('#export-json').disabled, true);
console.log('PASS: sample request ordering, stale worker results, threshold debounce, export guards, empty results, invalid input, and engine recovery (DOM/worker doubles).');
