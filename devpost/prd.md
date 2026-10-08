---
doc: prd
status: draft
implementation_authorized: true
review_basis: agent-authored details under explicit user delegation
---

# EndoScope AI — Product Requirements

A still-image polyp segmentation demonstration for teaching and research, with the medical department of Chongqing University identified by the learner as the intended audience.

Source: `scope.md > Who It's For`, `The Core Loop`, and `The POC Boundary`.

## Authorization and History

The learner approved the scope, then explicitly asked the assistant to make the remaining decisions and complete the work without further questions. The detailed choices below are assistant-authored under that authorization. They are not attributed to a completed learner-led PRD interview. This document is saved before the new implementation increment; `status: draft` preserves the distinction between permission to implement and a detailed learner review.

## The Core Journey

1. Open the public browser demonstration or start the desktop application.
2. Choose a credited example or an endoscopic image from the device.
3. Select Run analysis and see a clear loading message while the actual model runs.
4. Compare the original with the highlighted candidate mask and bounding boxes; inspect region areas and model scores.
5. Change the segmentation threshold to explore which pixels are included. The browser updates from its computed scores; the desktop asks the user to rerun.
6. Export a prediction overlay, binary mask, or JSON measurements.

Success means the displayed/exported result corresponds to the current image and threshold. It does not establish clinical accuracy.

## Screens and Layout

- Preserve the existing walkthrough page and browser-analysis page; add no accounts or dashboard.
- On a wide screen, show settings beside an original/result comparison and place region details below the images. Stack these areas on smaller screens.
- Preserve desktop controls and add the missing bundled example so Load test example is usable after download.
- Put a short three-step teaching guide near the browser workspace. Keep it separate from the image area.

## Look and Feel

Preserve the existing pale background, dark teal text, green prediction overlay, and readable sans-serif typography. Keep English labels, visible loading/error states, native keyboard-operable controls, and a prominent research-only notice. This retains the current prototype's identity; it is an implementation choice made under the learner's delegation.

## Features and Behavior

### Image Input and Examples

Users can select a local image or a clearly credited sample. The browser accepts images within 20 MB and 20 megapixels and explains local resizing for large permitted inputs. Opening another image clears stale predictions and disables exports until new results exist. Invalid images show a useful error without presenting the previous result as current.

### Real Inference and Results

Run the bundled trained model, rather than showing precomputed boxes. Display matching original/result dimensions, candidate count, region area, and model scores. Scores must be described as model outputs, not disease probabilities. A zero-region result says no candidates were found at that threshold and does not imply a healthy examination.

### Threshold Exploration

Explain that a higher threshold selects fewer pixels and may split connected regions. The number of boxes therefore need not decrease as the slider increases. Show the threshold used for every result. An unfinished slider update must not be exportable as if it were current.

### Export

Provide overlay PNG, binary mask PNG, and JSON. The JSON includes image dimensions, threshold, model hashes, and exclusive right/bottom bounding-box coordinates. Browser coordinates refer to the locally resized working image; include original dimensions too. Exports remain disabled before a successful current prediction.

### Reproducible Demonstration

Include the browser source, model, runtime, samples with attribution, and run instructions in the public repository. Serve it using a small local HTTP server without a compilation step. Keep the existing public URLs. Provide the existing recorded demonstration with readable English captions for upload to an accepted video host.

## States and Boundaries

- First use: identify the selected example and explain the next action.
- Loading: describe whether the model/engine is downloading or analysis is running; prevent duplicate runs.
- Image/engine failure: clear obsolete results, show a recoverable message, and allow another image or retry.
- Threshold update: disable exports until its result arrives.
- No candidates: preserve the valid empty mask and avoid a normal/healthy conclusion.
- Session boundary: input images and predictions live in device memory; no image-upload backend or account is added.

## Acceptance Criteria

- A fresh repository download contains a working desktop example and complete browser assets.
- The bundled model produces finite scores and correctly sized masks on the supplied example.
- On the demonstration image, thresholds 0.40, 0.85, and 0.20 reproduce the previously observed 4, 1, and 3 connected regions within the documented numerical tolerance.
- PNG and JSON exports agree on image dimensions and selected threshold.
- A newer image or slider request cannot be overwritten by an older asynchronous result.
- Runtime/model errors disable stale exports and explain a retry path.
- Captions describe only actions visible in the real recording; all assets retain credits.

## Product Decisions

Learner decisions: intended audience, polyp identification, teaching/research use, approved scope, and delegation of remaining implementation details. Assistant decisions: preserve layout and visual identity, use a concise teaching guide, and prioritize reproducibility and stale-result handling.

## Non-Goals and Open Items

No clinical diagnosis, inflammation/ulcer classes, live-video analysis, retraining, patient records, or additional service accounts. Native browser/desktop interaction and final learner feedback must be reported separately from automated checks. Public YouTube/Vimeo upload and learner-written submission answers remain shipping tasks.
