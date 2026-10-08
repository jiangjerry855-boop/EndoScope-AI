# Hackathon readiness record

Reviewed on October 8, 2026 (UTC). This is a technical status record, not a completed submission or a substitute for the Devpost Learn planning documents.

## Confirmed

- The GitHub repository is public.
- A complete MIT `LICENSE` is present and GitHub detects it as MIT.
- The desktop application source, required model checkpoint, and dependency list are present.
- The exact cloned checkpoint passed CPU inference and PNG/JSON export checks on one 599 × 507 sample image at thresholds 0.40, 0.85, and 0.20, producing 4, 1, and 3 candidate regions respectively. The check used Python 3.12.14 and PyTorch 2.6.0+cpu. This verifies a basic execution path, not detection accuracy.
- The demo page and browser-demo entry point returned HTTP 200 without signing in. Browser interactions were not tested in this check.
- The README now describes setup, operation, exports, and the limits of the repository.
- The `1-start` onboarding interview has been completed in the current AI-assisted workflow. Its personal learning context is kept separate from public project documentation.
- Personal onboarding context is excluded from Git commits by `/devpost/learner-profile.md` in `.gitignore`.

## Still required

- Verify a fresh dependency installation and the native desktop interface on the intended platform. The current repository check exercised inference and export in an existing environment, without opening the GUI.
- Agree on the project scope through the Skill Pack interview, then save and review a substantive `devpost/scope.md`.
- Complete and review `devpost/prd.md` and `devpost/spec.md` through the corresponding skills.
- Implement and verify the agreed work, record real progress in `devpost/checklist.md`, and complete hands-on review and the app map. Do not mark unperformed work complete.
- If the browser application forms part of the submitted project, include its required source and assets in the public code repository with run instructions.
- Upload a demonstration video shorter than three minutes to YouTube or Vimeo and make it publicly visible. A project-hosted video page alone does not meet that hosting requirement.
- Have the entrant write the submission fields and exit-survey answers. The curriculum permits AI spelling and grammar corrections, not AI-written replacements.
- Check the final entry, confirm its links work for a signed-out reviewer, and submit on Devpost before the deadline.

## Development history

The desktop prototype and hosted demonstrations existed before this actual Devpost Learn onboarding. They must not be described as having been created from the planning documents that will be written afterward. Record subsequent planning and implementation accurately, disclose incorporated prior work, and obtain organizer clarification if eligibility remains uncertain. This record does not establish or guarantee eligibility.

## Official references

- [Hackathon rules](https://learn-ai-basics.devpost.com/rules)
- [Devpost Learn Skill Pack and workflow](https://github.com/challengepost/learn-ai-basics)

The rules require a new project using the Skill Pack, an end-to-end working function, substantive scope/PRD/spec documents, a public repository with necessary code/assets/run instructions and an open-source license, and a public YouTube or Vimeo demo. The submission deadline is October 26, 2026 at 5:00 p.m. Eastern Time (4:00 p.m. Chicago time).
