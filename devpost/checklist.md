---
doc: checklist
status: draft
implementation_authorized: true
---

# Build Checklist

Build mode: fast, under the learner's explicit request to complete technical work autonomously. Planning details are assistant-authored under that delegation; no unperformed learner reviews are marked complete.

## Slices

- [x] **1. Run the same demonstration from the public repository**
  Becomes usable: The browser source and runtime are present, and the desktop sample button has a credited example.
  Why now: Makes the existing core workflow reproducible before adding guidance.
  PRD ref: `prd.md > Reproducible Demonstration`, `Image Input and Examples`
  Spec ref: `spec.md > Desktop Predictor and Example`, `Browser Interface`
  Build: Copy the complete static browser assets and add a public-domain desktop sample with attribution.
  Verify (mechanical): Check asset paths and hashes and run inference on the bundled example.
  Learner check: Open the app, load the example, and run analysis.
  Commit: `Package complete browser demonstration and desktop example`

- [x] **2. Explore predictions with clear guidance and current results**
  Becomes usable: A three-step guide explains the task, and stale results cannot be mistaken for the latest selection.
  Why now: Addresses first use and asynchronous interactions in the actual demo.
  PRD ref: `prd.md > Threshold Exploration`, `States and Boundaries`
  Spec ref: `spec.md > Browser Interface`, `Data and Export Contract`
  Build: Add guidance, guard image/sample ordering, and clear stale exports on failures or pending updates.
  Verify (mechanical): Exercise ordering/state helpers, JavaScript syntax, and actual worker processing.
  Learner check: Try a sample, a different image, and threshold changes; inspect errors and exports.
  Commit: `Improve teaching guidance and protect current-result state`

- [x] **3. Share verified source, a captioned recording, and a code map**
  Becomes usable: Reviewers have run instructions, evidence, visible limitations, and a real short demo.
  Why now: Packages the completed core workflow for review.
  PRD ref: `prd.md > Acceptance Criteria`, `Reproducible Demonstration`
  Spec ref: `spec.md > Verification`, `Where It Runs and How Someone Tries It`
  Build: Run checks, create the app map and captioned video, update documentation, publish source and the existing Site.
  Verify (mechanical): Confirm repository assets, numerical checks, video properties, and deployment results.
  Learner check: Open the published app and try the complete workflow.
  Commit: `Document verification and prepare demonstration materials`

## Hands-on Checkpoints

- [ ] Final user exploration of the updated app and feedback received

## Final Review

- [ ] User confirms the updated proof of concept is ready after trying it

## Code Tour and App Map

- [x] `devpost/app-map.html` generated from actual code and checked
- [x] A brief factual code-route recap and map delivered

Activity and evidence (October 8, 2026 UTC): the browser distribution and credited desktop example were packaged; the teaching guide and selection/request/export guards were implemented. Actual CPU and WASM inference, export consistency, asset hashes and DOM/worker-double state checks passed. `docs/VALIDATION.md` records exact results and untested GUI behavior. The 32.67-second English-captioned MP4 and offline code map were created. The existing public Site was updated successfully (version 2); the repository commit records the matching implementation and the runtime-parts launcher. Final learner practice is still open.

## Revisions

- The learner requested autonomous completion after approving scope. Detailed PRD/spec interviews and intermediate review pauses are not represented as completed learner activities; their technical plans remain transparently marked draft while implementation proceeds under that request.
