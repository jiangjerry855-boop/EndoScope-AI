# Validation record

Executed October 8, 2026 UTC against the repository increment described in `devpost/spec.md`.

## Executed checks

- `python scripts/verify_project.py`: model hashes, HTML asset links and DOM targets, vendored runtime files, caption timing coverage, a bundled desktop example, real CPU inference and PNG/JSON export.
- `node scripts/check_browser.mjs`: actual vendored ONNX Runtime Web WASM inference under Node; comparison to PyTorch on identical input; JavaScript image preprocessing, output restoration, thresholding, 8-connected regions, minimum area, empty output and exclusive box coordinates.
- `node scripts/check_ui_state.mjs`: application code with DOM/worker doubles, including reversed sample fetch completion, late worker messages, rapid threshold changes, disabled and guarded exports during pending updates, valid empty results, invalid/oversized files, and engine failure/retry state.
- JavaScript syntax checks: `web/demo.js`, `web/try/app.js`, `web/try/inference-worker.js`, and `web/try/processing.mjs`.

Environment: Python 3.12.14, PyTorch 2.6.0+cpu, NumPy 2.3.5, Pillow 12.3.0, SciPy 1.17.0; Node v24.19.0. Existing environment used; a clean installation was not tested.

## Actual inference results

Input: unchanged `01_polyp.jpg`, 599 × 507. No ground-truth mask is supplied.

| Threshold | Desktop regions | WASM regions | Desktop selected pixels | WASM selected pixels |
| --- | ---: | ---: | ---: | ---: |
| 0.40 | 4 | 4 | 94,792 | 94,807 |
| 0.85 | 1 | 1 | 53,643 | 53,675 |
| 0.20 | 3 | 3 | 127,930 | 127,933 |

Maximum absolute PyTorch/WASM output difference on identical model input: **0.00006548** (test limit: 0.0001). Pixel differences in the complete pipelines also include Pillow/JavaScript interpolation. The WASM pipeline here consumes Pillow-decoded RGBA bytes; real-browser image decoding was not tested. Box counts are observations for this image, not accuracy metrics.

All exported desktop PNGs are 599 × 507; mask pixels are 0 or 255. JSON dimensions and thresholds match the prediction. Region areas sum to selected mask pixels. Both model SHA-256 hashes match `web/assets/model-info.json`; the original checkpoint remains unchanged.

## Repository runtime packaging

The unchanged WASM engine is committed as two binary parts to fit the repository connector’s 16 MiB request limit. `scripts/serve_browser.py` verifies part and full-file SHA-256 hashes, reconstructs the runtime locally, then starts the standard-library HTTP server. Reconstruction into a fresh temporary directory was verified byte-for-byte against the inference-tested engine. No engine download is needed. The deployed Site serves the same complete runtime binary.

## Video

`web/assets/endoscope-demo.mp4` is the existing user recording, cropped to the application window without reordering its actions. `endoscope-demo-en.mp4` adds a 126-pixel footer with concise English captions and a research-use notice, preserving the image area. Its 32.67-second duration is unchanged. No music or invented UI actions are added. The recording starts with an image loaded and shows model reruns at 0.40, 0.85 and 0.20; it does not demonstrate completed export or the browser UI.

`python scripts/prepare_video.py` regenerates the English MP4 using FFmpeg/libass and DejaVu Sans. Frame inspection and FFprobe verify caption placement, dimensions and duration. This is a video-production check, not a browser test.

## Limits and hands-on follow-up

Live browser interaction, responsive visual layout, actual browser downloads, and native desktop GUI interaction were **not** exercised in this increment. The supported managed-browser QA capability was unavailable. DOM doubles and Node WASM computation are not substitutes for those checks. Fresh installation on Windows/macOS/Linux remains unverified.

For final hands-on review, open `/try/`, run a sample, move the threshold, choose another image, rerun, and open all three exports. Check that filenames, dimensions and settings describe the selected image. Try an invalid file and verify the previous result disappears. In the desktop application, use **Load test example**, run and export. No learner completion is claimed until feedback is received.

Reproduce with the three commands in the README. Machine-readable results are generated in `validation/` and summarized here; they do not establish diagnostic accuracy, generalization, or clinical suitability.
