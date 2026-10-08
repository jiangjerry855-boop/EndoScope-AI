# Hackathon readiness record

Updated October 8, 2026 UTC. This records completed technical work and remaining entrant actions; it is not a completed competition submission.

## Implemented in this increment

- Approved `devpost/scope.md`, prospective `prd.md` and `spec.md`, factual progress checklist, and offline `app-map.html`. The detailed PRD/spec remain agent-authored drafts under explicit user delegation; detailed learner review was not performed.
- Complete static browser source and assets in `web/`: trained ONNX model, vendored WASM runtime and MIT license, five credited samples, walkthrough recording, EN/ZH captions and English-captioned MP4.
- Public-domain desktop example, so **Load test example** works after repository download.
- Three-step teaching guide, explanation of threshold/region behavior, image request ordering, and guards against stale results and exports.
- Reproducible desktop inference/export, real WASM computation, asset/hash and simulated UI-state checks. See `docs/VALIDATION.md` for executed results and limits.
- README instructions for browser and desktop use. Browser use needs only a static HTTP server; no ML installation is needed for that path.
- Original model weights and desktop behavior preserved. Private learner context remains excluded from Git by `/devpost/learner-profile.md`.

## Still required before claiming submission readiness

- Entrant tries the published browser app and/or intended desktop platform, opens the exports, and supplies feedback. Live browser UI, actual download behavior and a fresh desktop dependency installation have not been verified in this increment.
- Entrant reviews the detailed planning and app map. Delegating implementation is not evidence that those learning activities were completed.
- Upload the demonstration to **YouTube or Vimeo** and make it publicly visible, then put that URL in the submission. The included 32.67-second English MP4 is prepared for upload. A project-hosted video alone does not satisfy the required hosting destination.
- Entrant writes their own personal submission responses and exit survey, reflecting work actually performed. The curriculum permits AI spelling/grammar help; do not invent personal experience or a completed planning interview.
- Disclose the earlier prototype and model and confirm organizer acceptance if eligibility remains uncertain. Added planning files do not establish eligibility.
- Verify the actual submission links for a signed-out reviewer, review the final entry, and submit it on Devpost. This workflow has not submitted an entry or contacted the organizer.

## Development history

The desktop prototype, model and initial hosted demonstration existed before the Devpost Learn planning phase. This phase first gathered the intended audience (medical-department teaching/research at Chongqing University), polyp-image use case and scope approval, then the entrant delegated detailed technical completion. The PRD/spec were saved before the repository/browser increment. No institutional adoption, affiliation or endorsement is claimed.

The new work packages the browser implementation, adds a usable example and teaching guidance, protects result state, supplies repeatable checks and prepares sharing material. Do not describe the planning documents as having guided earlier model development.

## Official references checked October 8, 2026 UTC

- [Official rules](https://learn-ai-basics.devpost.com/rules)
- [Devpost Learn Skill Pack](https://github.com/challengepost/learn-ai-basics)

Rules require a new working project using the Skill Pack, substantive planning documents, a public open-source repository containing necessary source/assets/instructions, English materials and a publicly visible YouTube/Vimeo demonstration shorter than three minutes. Deadline: **October 26, 2026, 5 p.m. Eastern / 4 p.m. Chicago**. The rules require disclosure of incorporated pre-existing work; acceptance is determined by the organizer.
