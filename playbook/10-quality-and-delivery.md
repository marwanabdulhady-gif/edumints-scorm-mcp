# Quality assurance and delivery

Maintain a `quality_checks` evidence table: source accuracy, asset completeness, accessibility,
responsive layout, audio synchronization, branching/scoring, SCORM, and video when present.
Use `pending`, `passed`, `failed`, or `not_applicable`. A status without evidence is not proof.
`not_applicable` requires a specific reason; do not use it to bypass an unperformed test.

Check every required manifest entry is registered and attached to its intended screens. Review
rights, meaningful alt text, captions/transcripts, character consistency and approved revision.
No planning-only/placeholder artifacts should be described as final production assets.

Run `lint_authoring_plan(..., stage='delivery')`, `lint_course`, preview desktop/narrow/RTL where
needed, inspect timing and media errors, and use `validate_package` after building. Test keyboard,
focus, readable text at small viewport, reduced motion and non-color clues. Do not promise that
`lock_until_complete` proves the learner listened to full audio; the current player has known
lifecycle limitations. Explicit cue markers in scripts are production intentions/estimated timings,
not guaranteed player keyword synchronization.

For games walk all meaningful routes and test wrong answers/hints/retry/resume/scoring. For SCORM
verify score, objectives, completion and resume in an appropriate test LMS or runtime probe.
A ZIP/manifest validation alone is not an LMS behavior test. Report unavailable browser/LMS tests
as pending, not passed. Revise the storyboard/scripts before replacing costly media unnecessarily.

Deliver the requested course ZIP or standalone media, asset map, source/revision notes, transcript,
QA evidence and disclosed limitations. Keep authored scripts/video source reproducible; avoid
committing bulky generated media or model binaries. Offer focused revisions with affected IDs.
