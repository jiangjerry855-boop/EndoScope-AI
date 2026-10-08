---
doc: scope
status: approved
---

# EndoScope AI

A teaching and research demonstration that identifies and highlights candidate polyp regions in endoscopic images.

## The Unique Kernel

Make the polyp model's output visible and inspectable: show the original image next to the predicted regions, and let the user see how a threshold change affects those regions. This is the defining demonstration, not a claim of a novel model architecture or clinical accuracy.

## Who It's For

The intended audience is people using endoscopic-image demonstrations for teaching and research in the medical department of Chongqing University (重庆大学医学部). The learner named this intended audience and agreed to the teaching/research scope. Actual institutional adoption, affiliation, or endorsement has not been established.

The immediate task is to inspect where the model identifies possible polyps in a still image. The audience's current workflow has not been described.

## The Core Loop

Open the demonstration, choose a permitted endoscopic image, run the model, and inspect the highlighted candidate locations and boundaries alongside the original. Adjust the threshold and rerun when exploring the prediction; export the mask, overlay, and measurements when a record is useful.

## Inspiration & Identity

Use the existing EndoScope AI prototype as the visual reference, with clearly readable images, a restrained interface, and a visible research-only label. The learner has requested English project materials and a simple browser version. Detailed visual decisions belong in the PRD.

- Current demo: https://endoscope-ai-demo.jiangjerry855.chatgpt.site/
- Current browser prototype: https://endoscope-ai-demo.jiangjerry855.chatgpt.site/try/

## Why This Matters to the Learner

The learner wants to make the polyp model usable through a demonstration and a simple web interface and prepare the project for the learning hackathon. Additional personal motivation has not been supplied.

## What "Working" Looks Like

A reviewer can follow the public repository's instructions, select a permitted sample image, obtain a real model prediction, and compare its marked locations and boundaries with the original image. They can change the threshold, rerun, and export an overlay, binary mask, and JSON result. The exported dimensions and settings match the selected image and controls.

The demonstration makes the effect of changing the threshold visible. A working execution path does not establish clinical accuracy. A short video must show actual application behavior.

## The POC Boundary

- Still-image polyp candidate segmentation for teaching and research.
- Original/result comparison, threshold adjustment, candidate-region details, and result export.
- A simple browser demonstration, with the source and assets needed to run it included in the public repository; preserve the existing desktop version.
- Clear setup and usage instructions, permitted demonstration material, and verification of the demonstrated workflow.
- Images processed on the user's device by the demonstration, without an image-upload backend.

The agreed next increment is to make the existing demonstrations reproducible from the public repository, supply a permitted example for the sample-image workflow, and complete the agreed checks and documentation. The PRD and technical plan must be reviewed before implementing this increment.

## Later

Further features and model improvements are undecided and require a separate scope decision.

## Explicitly Cut

- Clinical diagnosis or exclusion of disease: this project is a research prototype and has not established clinical performance.
- Inflammation or ulcer identification: the bundled model supports polyp candidates only.
- Live endoscopy/video analysis: a still-image workflow is sufficient for this proof of concept.
- New model training in this increment: the existing checkpoint already supports the core demonstration; the task is to package and verify that demonstration.

## Planning History

This scope was written after the learner identified the audience, requested polyp identification, and approved a teaching/research demonstration. On October 7, 2026 (America/Chicago), the learner reviewed the four-point scope summary and linked document and replied "可以" (approved). This marks approval of the scope; the PRD and technical specification remain to be developed.

The prototype and hosted demos predate this Skill Pack planning phase. This document plans the subsequent increment and does not claim to have guided earlier implementation. Hackathon eligibility is not established by adding this file.
