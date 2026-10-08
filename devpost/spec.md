---
doc: spec
status: draft
implementation_authorized: true
review_basis: agent-authored details under explicit user delegation
---

# EndoScope AI — Technical Specification

Implements the approved scope and the accompanying `prd.md`. Detailed technical decisions are made by the assistant under the learner's explicit authorization to complete the work. This is a prospective plan for the repository/demo increment, not a retrospective account of the earlier model development. Detailed learner review remains unrecorded.

## How This Works, In Plain Language

An image is reduced to the model's input size while keeping its proportions. The model assigns a score to each pixel. The threshold chooses which pixels to highlight, and neighboring selected pixels form candidate regions. The application draws those regions over the image and lets the user save the result. The browser performs this work on the user's device; a server only supplies program files.

## Where It Runs and How Someone Tries It

- Desktop: Python with Tkinter; install `requirements.txt`, then run `python app.py`.
- Browser, from a repository checkout: `python -m http.server 8000 --directory web`; open `http://localhost:8000/try/`. Do not open the HTML using a `file:` URL.
- Public browser URL: https://endoscope-ai-demo.jiangjerry855.chatgpt.site/try/
- Walkthrough URL: https://endoscope-ai-demo.jiangjerry855.chatgpt.site/
- Public source: https://github.com/jiangjerry855-boop/EndoScope-AI

## Desktop Predictor and Example

Implements `prd.md > Image Input and Examples` and `Real Inference and Results`.

Keep `app.py` and `endo/` as the desktop application. Preserve the current Compact U-Net and checkpoint SHA-256. Add a credited public-domain example under `examples/` so the existing sample button works. Use the existing `Predictor` and export routines for a reproducible smoke check. Do not retrain or change model weights.

## Browser Interface

Implements `prd.md > Screens and Layout`, `Threshold Exploration`, and `Export`.

Copy the current static Site into `web/`, retaining the same root-relative paths. `web/try/app.js` owns the image, active request, displayed result, and export buttons. Add a three-step instructional section and concise threshold explanation. Make image/sample request ordering explicit so an older request cannot replace a newer image. Clear or disable stale results on failures and while a new result is pending.

## Browser Inference Worker

Implements `prd.md > Real Inference and Results`.

`web/try/inference-worker.js` uses vendored ONNX Runtime Web 1.30.0 with one WASM thread and a dedicated worker. `processing.mjs` performs RGB normalization, bilinear letterboxing to 160 × 160, output restoration, and 8-connected component extraction with a 16-pixel minimum. Preserve the ONNX model converted from the desktop checkpoint. Cache pixel scores for threshold-only updates.

## Data and Export Contract

Implements `prd.md > Export` and `States and Boundaries`.

- Inputs and results stay in memory; no user-image network upload or persistence is introduced.
- Browser files: at most 20 MB; decoded images at most 20 megapixels; working images capped at 4 megapixels and a 4096-pixel longest side.
- Boxes use `[x1, y1, x2, y2)` with exclusive right and bottom coordinates.
- Browser JSON includes original and working dimensions, threshold, model identifiers, region details, and research-only notice.
- PNG exports use working-image dimensions; desktop exports use original-image dimensions.
- Small browser/Pillow decoding and interpolation differences remain documented.

## Look and Feel

Keep the existing CSS and responsive layout. Add the instructional section using the existing palette, spacing, and native HTML elements. No new framework, font service, analytics, account system, or database is needed.

## File Structure

| Path | Responsibility |
| --- | --- |
| `app.py`, `endo/` | Existing desktop application and predictor |
| `models/` | Original model checkpoint and training records |
| `examples/` | Credited desktop example |
| `web/index.html`, `web/demo.js`, `web/styles.css` | Captioned walkthrough and shared styling |
| `web/try/` | Browser analysis UI, worker, and image processing |
| `web/assets/` | ONNX model, WASM runtime, images, licenses, recording and subtitles |
| `scripts/verify_project.py` | Desktop inference/export and static asset checks |
| `scripts/check_browser.mjs` | Processing and actual WASM inference checks under Node |
| `docs/VALIDATION.md` | Executed checks and their limitations |
| `docs/HACKATHON_STATUS.md` | Remaining submission requirements |
| `devpost/` | Scope, PRD, spec, build checklist and app map |

## Verification

Start a plain local HTTP server only where the supported preview workflow permits. Independently validate JavaScript syntax, required files, HTML asset references, model hashes, worker processing, thresholds, and actual WASM outputs under Node. Run desktop inference and export against the bundled example. Verify the finished video's duration and caption placement.

The managed Site workflow requires its supported browser-control capability for browser QA. If unavailable, do not substitute unapproved browser automation: report that UI interaction remains unverified and continue mechanical checks and deployment. Headless computation tests are not described as browser UI tests. The user recorded the earlier desktop prototype, but that does not prove a fresh installation of this increment.

## Build Slices

1. Publish this prospective plan and copy the complete browser distribution and credited example.
2. Add teaching guidance and repair asynchronous/stale-result handling with focused verification.
3. Run model/export/asset checks, prepare the captioned recording and offline app map, then publish the verified repository and Site changes.

## Decisions and Open Issues

- Retain the current framework-free architecture and trained model to preserve the approved small scope.
- The learner did not name a technical learning uncertainty; no learning outcome is invented.
- A complete local planning interview and detailed document review were delegated rather than performed; this distinction remains explicit.
- The earlier prototype predates these documents. Organizer acceptance of this development sequence remains unconfirmed.
- External video upload, final user exploration, and personal submission reflections require actual completion before being marked done.

## Dependency References

- Python/Tkinter: https://docs.python.org/3/library/tkinter.html
- PyTorch: https://pytorch.org/docs/stable/index.html
- Pillow: https://pillow.readthedocs.io/en/stable/
- NumPy: https://numpy.org/doc/
- SciPy: https://docs.scipy.org/doc/scipy/
- ONNX Runtime Web: https://onnxruntime.ai/docs/get-started/with-javascript/web.html
- Model conversion: https://pytorch.org/docs/stable/onnx.html

The exact current prototype assets and installed package versions are the implementation baseline; these links are dependency documentation, not evidence of a newly surveyed version recommendation.
