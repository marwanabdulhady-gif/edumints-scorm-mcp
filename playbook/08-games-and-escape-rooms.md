# Gamification, scenarios and escape rooms

Start with a measurable objective and source evidence. A puzzle should require applying what
was taught, not guessing a password or reading arbitrary trivia. Record an `ActivityPlan` with
screen, objective/source links, instructions, required props, success/scoring rules, feedback,
failure/retry behavior, and a keyboard/text alternative. Explain each reward's learning purpose.

For an escape room, design: premise/mission; rooms or puzzle chain; clue placement and discoverability;
accepted solutions/aliases; at least one graduated hint; dependencies; failure/retry and lives;
completion condition; explanatory debrief; optional timer policy. All assessed clues must be
available to the learner. Hints must be text-accessible; audio/color cannot be the only clue.

Use supported surfaces:
- `escape_room`: sequential text-answer puzzles with accepted answers, hints and lives.
- `game`: compositional nodes/choices, score/lives/hints/timer and declarative rules.
- `decision_scenario`: branching decisions with consequences and rationale.
- `sorting`, `matching`, `mcq`, `simulation`: focused practice instead of gratuitous game layers.

Inspect `list_screen_types`, schemas and `docs/GAME-PATTERNS.md`, `GAME-A11Y.md`, and
`GAME-ANTISLOP.md`. Decorative maps/props do not imply an arbitrary spatial escape-room engine.
Do not promise persistent inventory, independent exam attempt limits, or sound triggers without a
supported contract. A final exam pool/retry orchestrator is not supplied by this playbook.

For timed composed games, allow extend/disable; avoid unadjustable screen timers. Prefer keyboard
sorting/matching over pointer-only drag/drop. Show mission, rules, puzzles, answers, hints,
feedback and debrief for approval before producing props or audio. Walk every route: success,
wrong answer, hint use, exhaustion, restart and resume; verify scoring cannot inflate on replay.
