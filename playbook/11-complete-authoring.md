# Complete module production contract

The `AuthoringPlan` is a **planning document**, not a `CourseSpec`. Copy the filled example
returned by `get_playbook('authoring')`. Keep it in the client's workspace; this lint tool does
not save it in the server database or automatically assemble a course from it.

Required spine: module ID/revision/title/language/audience, reference analysis, learner journey,
sources, objectives and `visual_plan`. Add `narration_script` for narration. Expand optional
assets/characters/activities/videos for the requested deliverable—not every course needs a game.

| Section | Required detail |
|---|---|
| sources | stable ID, location, observed facts, reuse policy, permissions if reusing assets |
| objectives | observable outcome, source IDs, assessment screen IDs |
| visual_plan | actual screen type, learning purpose, composition, text, imagery/alt, cue intentions |
| assets | kind, screen links, detailed production brief/route, provenance/rights, text alternatives, status |
| characters | role, identity/style invariants, master reference, required variants |
| activities | objectives/evidence, rules/score/success/failure, feedback, keyboard alternative; escape hints/solution/debrief |
| videos | engine/reason, workspace/server route, license review, shots, output/caption assets |
| reviews | scope, current revision approval status, reviewer and actual approval evidence |
| quality_checks | named acceptance category, status and test evidence or a justified not-applicable reason |

Run `lint_authoring_plan(plan, stage)`:
- `planning`: validate cross-references, text alternatives, character coverage, escape completeness,
  video route/limits and existing visual/narration checks. Approval/production status can be pending.
- `production`: additionally require recorded user approval for applicable scopes and engine-license
  confirmation. **Actually ask the user**; fabricated review records are not acceptable.
- `delivery`: additionally require all planned assets registered and applicable QA checks evidenced.

Every revision resets affected reviews/QA in your document. The checker does not authenticate the
reviewer, compare prior revisions, inspect binaries, verify server asset existence, or gate unrelated
build/TTS calls. Keep approvals truthful and distinguish checklist validation from execution proof.

After approval, translate screen planning into supported `CourseSpec`/`add_screen` payloads. Map
planning asset IDs to real returned server IDs. Preserve objectives/evidence links; do not pass this
entire planning document to `build_from_spec`. With scenario tools, compile then explicitly carry
language/voice settings into the returned course spec (scenario defaults may otherwise be Turkish).
