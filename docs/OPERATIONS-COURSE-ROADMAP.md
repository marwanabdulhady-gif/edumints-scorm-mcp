# Operations-course roadmap: verified gaps and delivery plan

- **Audit date:** 2026-10-14
- **Repository:** `marwanabdulhady-gif/edumints-scorm-mcp`
- **Baseline:** `ce10d1f835787288430dd40d05bbb7e6bd427b9f`
- **Status:** Planning only. No feature implementation, PR merge, or distribution change is authorized by this document.

## Executive recommendation

Keep the deterministic compiler architecture. Build a **shared authored-cue and narration-lifecycle foundation**, then make **`process_flow` the first new screen type**. Ship resources, transcript access, and English/Arabic authoring support alongside that pilot. Implement hub navigation and a scoped final assessment before investing in a general canvas editor/import pipeline. Treat automatic alignment and paid TTS providers as separate, optional integrations.

The proposed roadmap is directionally sound, but several gaps are narrower than the handoff suggests—and two claimed guarantees are not present: reliable audio-end locking and server-enforced approval of the visual plan/script.

### Scope and evidence limits

- Inspected models, renderer, player JavaScript, validation, packaging, MCP entry points, existing tests, and the open playbook PR diff.
- The Menabev/Storyline package itself was **not supplied in this session**. Slide counts, asset counts, percentages, timing quality, and its reported navigation defect are supplied context, not independently verified findings. Do not promise a particular slide-count reduction from this audit.
- [PR #1](https://github.com/marwanabdulhady-gif/edumints-scorm-mcp/pull/1) was **open** at inspection, head `260041983571713874bbfea8fcf925bb851a8643`. Its `playbook/`, models, five tools, and two prompts are **not in this baseline**. Its diff was read; its branch was not applied or tested here.
- “Supported” below means a repository capability, not a claim that a deployed server or a particular LMS has been exercised.

## 1. Corrected gap list

| Proposed item | What exists now | Actual gap / verdict |
|---|---|---|
| **1. `process_flow`** | `timeline`, `worked_example`, `simulation`, `sorting`, branching scenarios, display-mode `labeled_diagram`, and server-rendered SVG charts | **Confirmed native gap.** No process graph, lanes, connectors, or shared walkthrough/explore/sequence specification. An authored SVG can be displayed today, but that is not a structured process component. |
| **2. Authored cue timing** | Automatic reveal, click reveal, paced fallback, audio playback controls, animation presets | **Confirmed, with prerequisites.** No course-screen `cue_sec` or alignment tool. Reveal units do not consistently correspond to authored blocks, and audio locking needs a correctness pass. |
| **3. `canvas_slide`** | Configurable 960×540 stage; split/full-media content layouts; positioned and timed elements in the **separate MP4 composition pipeline**; sandboxed `embed_html` | **Confirmed native course-screen gap**, not an absence of all positioning support. Reuse concepts, not the MP4 renderer or unrestricted HTML as a shortcut. |
| **4. Final exam** | Graded questions, objectives, pass mark, results breakdown, seeded RNG/item-bank primitives, adaptive item selection | **Confirmed orchestration gap.** No assessment-scoped pool/draw, attempts, review policy, submitted state, or scoped retry. The bank primitive is a building block, not an existing exam. |
| **5. Hub** | `branching` can route to other screens; outline menus track visits; hotspot explore tracks region visits | **Confirmed reusable-component gap.** No tile-to-subsequence contract, automatic return, or persistent per-spoke completion rule. A manually authored branching approximation is possible. |
| **6. Resources + transcript** | PDF asset ingestion/packaging; per-screen `narration_text` in the CC bar; author-supplied WebVTT on `video` | **Partial gap.** Add a course resource catalogue and course-wide transcript panel. Do not rebuild captions or claim there is currently no transcript text. |
| **7. Market voices** | `synthesize_speech(..., voice=...)`, `CourseSpec.tts_voice`, `auto_tts`, and uploaded external narration | **Partial gap.** Course-level voice selection already exists for one-shot builds. Missing: bundled/catalogued English/Arabic voices, language-aware checks, persistent voice preference for iterative authoring, and optional providers. Arabic UI localization is also missing. |
| **8. SOP recipe** | Scenario planning/compilation, evidence-to-question links, outlines, media slots, quality lint; README links to an external authoring skill | **Authoring-pattern gap, not an AI-server gap.** Add a portable SOP recipe and examples using those contracts; keep content reasoning in the client. |

### Source anchors

- Screen schemas, reveal fields, stage dimensions, voice input: [`core/project.py`](../core/project.py#L363) (`ScreenType`, `ScreenBase`, `ContentBlock`, `CourseSpec`, `Project`).
- Existing instructional alternatives: [`SortingScreen` / `TimelineScreen` / `SimulationScreen`](../core/project.py#L620), [`LabeledDiagramScreen` / `ResultsBreakdownScreen`](../core/project.py#L780), [`AdaptivePracticeScreen`](../core/project.py#L906).
- Rendering and scoring config: [`_course_config`](../components/renderer.py#L616), [`_effective_reveal` / `_wrap_blocks` / `_r_content`](../components/renderer.py#L869).
- Timing, completion, and results: [`components/templates.py`](../components/templates.py#L1106) (`viewedAll`, `renderResultsIfNeeded`, `onScreenEnter`, `distributeCues`).
- Existing selection primitives: [`itembank.js`](../components/engine/primitives/itembank.js), [`rng.js`](../components/engine/rng.js). The bank uses `prompt`/`answer`/`distractors`, not the `MCQScreen` schema.
- Video-only positioned elements: [`core/video.py`](../core/video.py), [`components/video_compiler.py`](../components/video_compiler.py).
- Asset packaging: [`Packager.build_sync`](../core/packager.py#L172); PDF MIME support: [`auth/ssrf.py`](../auth/ssrf.py#L28).
- Speech: [`core/tts.py`](../core/tts.py), [`synthesize_speech`](../server.py#L998), [`build_from_spec` auto-TTS path](../server.py#L1358), [`Dockerfile`](../Dockerfile#L35).
- Planning: [`core/scenario.py`](../core/scenario.py#L182), [`scenario_compile`](../server.py#L1732). External skill location: [`README`](../README.md#L64).

## 2. Prerequisites the original proposal misses

### A. Playbook guidance is not workflow enforcement

PR #1 adds independently callable lint/export tools and prompts. It does **not** add approved-plan/script state to `Project`, nor approval checks to `synthesize_speech`, `build_from_spec` (including `auto_tts`), or `build_package`. A client can still bypass those tools. Exposing a prompt does not guarantee every connected agent loads or follows it.

Its exported cue times are **word-count/pause estimates**, not timestamps measured from audio. Nothing in that PR connects those estimates to the player. “Blocks in the same order” cannot guarantee keyword-level synchronization.

Before integration, choose and document one of these contracts:

1. **Advisory workflow:** prompts and validation reports guide cooperative clients. Describe it honestly as guidance, not mandatory approval enforcement.
2. **Opt-in enforced workflow:** persist versioned brand/plan/script records and approvals tied to their content digests; invalidate approval when approved inputs change. Gate every relevant server entry point **before** audio generation or packaging, including one-shot `auto_tts`. Establish an authenticated reviewer boundary: an authoring agent setting `approved: true` is not proof of human approval. Preserve legacy behavior for projects not using the policy.

The server cannot prevent audio being generated by an unrelated external service. It can enforce acceptance/build policy for artifacts entering its own workflow. Security/authorization changes require explicit maintainer review. Also check that playbook templates ship in every supported installation form; the PR adds Docker copying, but the current wheel configuration does not explicitly include `playbook/`.

### B. Narration and reveal need separate lifecycle state

Code inspection and isolated probes of the **actual** timeline JavaScript found:

| Observation | Evidence / consequence |
|---|---|
| Three reveal units with an 8-second audio duration receive cues `[0, 2, 4]`; `TL.done` becomes true at 4 seconds, before `ended` | [`showUpTo`](../components/templates.py#L2173) equates last-element reveal with completion. That cannot implement “wait until narration ends.” |
| Next is not initially disabled by `onScreenEnter` in the same probe | [`checkLock`](../components/templates.py#L2132) is not an entry-time navigation guard; [`next` / `goId`](../components/templates.py#L1260) also do not enforce this field themselves. A disabled button alone is insufficient. |
| With `reveal: "none"`, the timeline returns before attaching narration audio to the player | [`onScreenEnter`](../components/templates.py#L2168). Interactive screens default to this reveal mode, so narration support must not depend on visual reveal being enabled. |
| A title plus three `ContentSlide.blocks` entries renders as **two** reveal units: title and the entire content stack | [`_r_content`](../components/renderer.py#L981) nests all entries inside `.content-blocks`; [`_wrap_blocks`](../components/renderer.py#L919) wraps the outer container. Three top-level `body_html` paragraphs instead render as title plus three units. |

These are bounded model/render/function probes with DOM/media stubs, **not a browser or LMS playback test**. Add real-browser regression coverage before shipping a fix. The existing [`test_timeline_cues.mjs`](../tests/test_timeline_cues.mjs) tests a copied distributor function, not the player lifecycle.

### C. Existing completion/scoring semantics are not an exam or hub contract

- [`viewedAll`](../components/templates.py#L1119) accepts `state.reachedEnd` as an alternative to visiting every screen. Reaching the last screen must not bypass an opted-in hub or assessment requirement.
- Outline sequential unlock is deliberately based on **visits**, not audio completion or passing a quiz ([`progress.js`](../components/engine/progress.js)). Do not silently redefine that existing behavior.
- Course scoring currently sums all configured quiz points. Randomly drawing 12 of 30 questions needs an active-assessment denominator; unselected questions must not lower the score or remain required navigation stops.
- Results breakdown currently computes percentages from **answered** result entries ([`renderResultsIfNeeded`](../components/templates.py#L1301)). An assessment summary needs explicit rules for unanswered questions and submission.
- Suspend recovery can retain aggregate score/objective snapshots even when detailed results are trimmed. A retry that only deletes question results can leave an old score floor in effect. Design scoped attempt state and recovery together ([`scorm.js`](../components/engine/scorm.js#L454)).

### D. RTL support does not mean a localized Arabic product

[`components/i18n.py`](../components/i18n.py#L276) contains maintained English and Turkish tables only. Arabic gets RTL layout but English fallback controls (the audit probe returned `Next` for Arabic). Add Arabic player strings and human language QA, not just an Arabic voice.

The scenario document/compiler also does not currently carry course language or voice settings. Until that is extended, an English/Arabic recipe must compile first, add `language` and the desired TTS settings to the returned spec, then call `build_from_spec`; it should not blindly use `compile_and_build=True` and inherit Turkish defaults.

## 3. Implementation slices and acceptance criteria

All API shapes below are **proposals**, not supported inputs today. New course models belong in `core/project.py`; prefer separate modules for pure layout/state logic.

### 1 — Native process flows

**Scope:** stable lane and step IDs; action/decision/terminal kinds; explicit directed edges with labels; optional system reference, exception indication, details, and cue targets. Use IDs for references, not translated lane names. Define where lane-less decisions appear rather than relying on accidental layout.

Split delivery:

- **Walkthrough:** deterministic SVG connectors/lane layout with readable step labels and an equivalent semantic HTML sequence. A supplied graph must yield the same layout; no server-side content generation.
- **Explore:** keyboard-operable step buttons and sanitized details; explicit completion policy. Exceptions need text/icon treatment, not color alone.
- **Sequence quiz:** reuse ordering interaction/scoring concepts, but require an explicit linear path or assessed subset. A branching/cyclic SOP does not have one universal correct ordering. Reject ambiguous quiz specs rather than invent an answer key.

Validate duplicate IDs, dangling lanes/edges, unreachable steps, missing decision outcomes, and the chosen cycle policy. Bound graph size and provide a stacked mobile layout rather than shrinking a dense diagram into unreadable text.

**Acceptance:** one supplier-receiving example with a decision and exception; model/graph tests; deterministic render tests; English/Arabic layout and keyboard checks; walkthrough/explore excluded from quiz totals; sequence mode reports a SCORM `sequencing` interaction exactly once and contributes only its intended points. Add an MCP build test and visual fixtures for the modes.

**Dependencies / effort:** cue foundation for narrated walkthroughs; explicit scoring integration for quiz mode. **Large**, best delivered in separate walkthrough/explore and quiz slices.

### 2 — Authored cues first; automatic alignment later

**2A: native authored timing.** Add optional stable targets and finite, non-negative `cue_sec` values to typed content blocks/hotspot regions and to new flow/canvas elements. Preserve `distributeCues` when timing is absent. Define mixed authored/automatic timing, ties, untimed headings, duration overflow, and click/no-audio behavior explicitly; never silently redistribute authored timestamps. The current `ContentBlock` model drops an unknown `cue_sec` key, so adding it to an agent's JSON or instructions alone will not enable timing.

Separate `reveal_complete`, `audio_ended`, and interaction completion. Use a shared navigation decision for Next, menu jumps, keyboard actions, and scripted routes where a policy applies. Agree what “complete” means after seeking, replay, resume, an audio error, or a learner accessibility override—playing to the last cue is not listening to the narration. Provide a usable fallback when autoplay or audio loading fails.

**2B: optional alignment adapter.** `align_narration(project_id, screen_id)` could read the exact attached audio and transcript and return word/segment offsets, timing source, backend/version, and mismatch diagnostics. Keep applying cues an explicit author action. Cache against audio bytes, transcript, language, and backend settings; changing audio invalidates timing.

The current Piper wrapper returns WAV bytes only. Do **not** promise native word timing or select `aeneas`/`whisper-timestamped` without a capability/licensing/English-and-Arabic accuracy spike. Alignment is a best-effort speech-processing operation, not an exact guarantee. Pin backend/model versions, bound resources/timeouts, keep dependencies optional, and never relabel estimated timing as measured alignment. Align against final audio or prove that subsequent processing preserves timing.

**Acceptance:** actual player tests for cue boundaries, zero/tied/mixed cues, seek backward/forward, pause/replay/back navigation, reduced motion, audio errors, and narration with reveal disabled; preview/package parity; legacy untimed output preserved except separately approved bug fixes. Alignment additionally needs a small annotated bilingual corpus and a stated error tolerance.

**Dependencies / effort:** **Medium–large** for 2A; **uncertain/large** for 2B. Automatic alignment is not a prerequisite for shipping authored cues.

### 3 — Native canvas slides

**Scope:** an opt-in `canvas_slide` whose ordered elements have stable IDs, numeric stage coordinates/bounds, an image asset or sanitized HTML content, accessible text, restricted animation presets, and optional entry/exit timing. Use existing `stage_width`/`stage_height`, rather than hard-coding a second 960×540 coordinate system.

- Keep reading/focus order independent of visual stacking. Require text alternatives for meaningful imagery and explicit decorative status.
- Keep real text as HTML. Validate coordinates, dimensions, asset references, and `exit_sec >= cue_sec`; do not expose arbitrary scripts or unrestricted CSS as the layout API.
- Provide a semantic reflow mode for small screens/zoom. The existing stage player already switches to flow when scaling would make content too small.
- Treat image-layer import as **author-supplied assets plus layout metadata**. A flat Canva/Figma export does not contain recoverable editable layers. Direct design-file or Storyline import is separate scope.
- Borrow ideas from `VideoSpec`, but do not route course rendering through the MP4/GSAP pipeline, which has different units and delivery/accessibility requirements.

**Acceptance:** layered bilingual example with selectable text; stable z-order and cue/exit behavior; sanitizer regression tests; no focusable hidden layers; narrow-viewport/reduced-motion tests; self-contained package with provenance for imported media.

**Dependencies / effort:** authored cues and an approved accessibility/reflow contract. **Large**; defer until the SOP pilot proves a need beyond process flows and existing content layouts.

### 4 — Assessment-scoped exam

**Scope:** a dedicated assessment configuration referencing question IDs, with pool, `draw_count`, option-shuffle policy, passing threshold, attempt limit, review policy, and explicit submit/results/retry transitions. Prefer this over overloading an outline node's navigation flag.

Key design decisions:

- Reuse the seeded RNG and, where appropriate, adapt the item-bank selection logic. Its data shape is not a drop-in replacement for authored MCQ screens.
- Persist selected IDs, option order, responses, submission state, and attempt number. Reloading must not redraw questions or reset the attempt counter. Define whether Retry redraws.
- Separate formative practice from the final-exam denominator and define which score contributes to LMS success. Unanswered selected questions cannot disappear from the denominator.
- Suppress premature correctness/answer disclosure according to review policy, not just a results-screen label.
- Reset **local state for that assessment attempt only**. SCORM is not a database in which prior `cmi.interactions` rows can simply be deleted. Choose documented attempt-qualified interaction IDs/history behavior; do not erase unrelated progress or evidence.
- Define recovery when suspend data is truncated or the course is republished. Do not silently award extra attempts or revive a previous attempt's aggregate score.
- Decide whether the limit applies within one LMS attempt or across registrations. A self-contained browser package is **not tamper-proof**; high-stakes attempt enforcement belongs in the LMS/authorized assessment service.

**Acceptance:** 12-from-30 fixture; stable resume midway through an attempt; correct denominator; failed attempt → permitted retry → exhausted limit; successful pass; review behavior; no repeated-submit inflation; unchanged non-assessment results; SCORM 1.2/2004 interaction/objective/completion probes and suspend-size tests.

**Dependencies / effort:** agreed completion/state contract and maintainer approval for scoring/suspend changes. **Very large / highest regression risk**. Separate model/selection, runtime/resume, and reporting/retry work.

### 5 — Hub and spokes

**Scope:** tiles reference existing screen sequences or outline nodes, with an entry, a defined end/return, and a required/optional status. Avoid a second set of nested screen objects or duplicate IDs.

Track not-started/in-progress/completed separately; entering a tile alone must not complete a narrated multi-screen spoke. Persist a compact return context and progress, and restore focus to the launching tile. Define overlapping spokes, nested hubs, cycles, back/menu exits, and interactions with sequential outline locks; a first version can reject nesting/overlap.

**Acceptance:** three-spoke fixture with separate narration; complete in any order; leave/reload mid-spoke and return correctly; ticks survive resume; required spokes cannot be bypassed by visiting the final screen; keyboard/focus and RTL tests; no regression in ordinary branching.

**Dependencies / effort:** shared completion/navigation decisions, not necessarily the whole exam feature. **Large**. Keep hub and assessment implementation PRs separate even where design work is shared.

### 6 — Resource catalogue and course transcript

**Scope:** optional top-level `resources: [{asset_id, title, ...}]` on both `CourseSpec` and persisted `Project`, plus an opt-in accessible player panel. Reuse asset storage and manifest packaging. Resolve resource links through the asset map to `href`/download targets; the current generic `data-asset` resolver assigns `src`, so attaching it unchanged to an anchor is insufficient.

Build transcript sections from original `narration_text`, in screen order, with screen headings. If transcript navigation is offered, honor the same navigation policies as the player. Clearly distinguish this static course transcript from timed video captions or future aligned narration captions. Provide a helpful missing-text indicator/warning instead of pretending audio-only screens have transcripts.

**Acceptance:** packaged PDF opens/downloads offline; preview links work; dangling resource references fail validation; panel opens/closes by keyboard and returns focus; text is escaped; narration markers/pronunciation substitutions do not leak into learner text; resource reading does not alter scores; no panel or output changes when the feature is absent.

**Dependencies / effort:** independent of process-flow/assessment work. **Small–medium**; suitable for an early delivery lane.

### 7 — English/Arabic delivery

**Scope:** preserve existing `voice` and `tts_voice` inputs. Add a discoverable catalogue of installed voice IDs/locales, clear missing-model/mismatched-language diagnostics, and optional persistent course defaults for iterative authoring. The current `voice` value resolves to a server-local model path; a friendly catalogue is a usability improvement, not a new TTS engine.

- Current Docker provisioning downloads only `tr_TR-dfki-medium`. Choose English and Arabic models after checking availability, model cards, redistribution terms, engine license obligations, checksums, and pronunciation quality. Do not put model binaries in Git.
- Do not silently generate Turkish narration for an English/Arabic course. Preserve/document legacy behavior unless a stricter policy is explicitly enabled. `auto_tts` currently skips missing Piper/models without failing the build; make capability reporting clear.
- Add Arabic player strings, Arabic-capable font coverage, mixed-direction SAP/MIGO labels, and human review of Arabic pronunciations. An `ar_JO` model name alone does not guarantee the desired Saudi/Gulf delivery.
- Uploaded narration already enables external/human voices today. Add a paid provider only if server-side orchestration is needed, as an explicit plugin with deployment-managed credentials, cost limits, privacy/consent expectations, and a declared timing/SSML capability contract. Keep the offline route.

**Acceptance:** mocked provider/capability tests; opt-in real synthesis smoke tests with approved models; no-audio-generation without required workflow approval; voice preference round-trip if added; `language` propagation through the chosen authoring path; Arabic labels/RTL/font checks and pronunciation sign-off.

**Dependencies / effort:** catalogue/localization **medium**; extra providers a separate **medium** integration. Voice quality/licensing remains unverified in this audit.

### 8 — SOP-to-course authoring recipe

**Scope:** a portable client-side recipe: source inventory and SME confirmation → objectives → process overview → section hub (or current branching/outline fallback) → trigger/actors/preconditions → walkthrough → system update → exceptions → formative scenario → final assessment → resources.

Use existing scenario pages, `screen_payload`, media slots, `evidence_from`/`evidence_screen_ids`, and quality reports instead of inventing another parallel course model. Preserve traceability to SOP sections and version; do not let the agent invent undocumented operating steps. Distinguish practice from assessed evidence.

If PR #1 is adopted, a natural home is `playbook/recipes/sop-to-course.md` plus filled templates; link or port it to the external authoring-skill repository through a separately authorized change. Explain which features require which server version and supply a current-capability fallback. Keep plan/script approval and pronunciation review before audio production.

**Acceptance:** one complete receiving-process recipe/example with source references, an exception, a rationale-rich scenario question, and an explicit exam blueprint; existing schema/lint passes for the fallback; native-feature examples become build/MCP fixtures only as those features ship. No server-side LLM or automatic pedagogical decisions.

**Dependencies / effort:** draft now against existing features; extend as native capabilities land. **Small** for recipe content, separate from new runtime work.

## 4. Recommended delivery order

Sizes are relative scope/risk, **not time estimates or delivery commitments**.

| Milestone | Work | Exit condition |
|---|---|---|
| **M0 — Contract and baseline** | Decide advisory vs enforced approvals; review PR #1; agree narration completion/seek policy, exam scope, and distribution ownership. Record the runtime defects above as focused work. | Approved contracts; no claims of measured alignment, mandatory approvals, or audio-end locking without evidence. No automatic PR merge. |
| **M1 — Narration foundation** | Item 2A: stable cue targets, authored timing, independent audio lifecycle; focused locking/navigation regression fixes. | Actual player tests demonstrate timing and agreed completion behavior, including failure/accessibility paths; legacy changes explicitly reviewed. |
| **M2 — Process pilot** | Item 1 walkthrough/explore, then a separately reviewed sequence-quiz slice. | A supplier-receiving teaching/practice module builds and runs in 1.2/2004 with correct semantics and responsive layouts. |
| **Parallel early lane** | Items 6, 7 (catalogue/Arabic UI), and 8. Start the recipe with current types; extend after M2. Serialize overlapping hot-file edits. | Packaged SOP resource + transcript, explicit English/Arabic configuration, and a usable end-to-end authoring recipe. |
| **M3 — Navigation and final exam** | Item 5 hub, then item 4 exam slices, sharing the approved completion/state design. | Spoke return/resume and 12-from-30 attempt/retry/reporting tests pass; incomplete work cannot become completed via navigation shortcuts. |
| **M4 — Designer composition** | Item 3 canvas; author-supplied layer metadata, not a general Figma/Canva/Storyline importer. | Accessible, timed, responsive composed slides justify their added complexity. |
| **M5 — Optional speech automation** | Item 2B alignment spike/adapter; item 7 paid-provider plugins if needed. | Bilingual timing/quality and licensing criteria met; deterministic inputs/versioning and explicit unavailability behavior verified. |

**First implementation recommendation:** authorize M1 as the prerequisite correctness/timing task, followed by M2 as the first new screen capability. Do not bundle eight features, a rebrand, and approval enforcement into one PR.

## 5. Integration and release guardrails

- **Additive contracts:** default new fields to absent/disabled; preserve existing MCP signatures/returns and stored-project loading. Update both one-shot and incremental paths where a feature is intended to persist.
- **New screen checklist:** `ScreenType`/discriminated union; renderer dispatch/config; scored vs unscored mode handling; reference/asset/graph validation; scenario compilation; anti-slop/evidence rules; discovery descriptions; English/Turkish strings plus Arabic delivery work; `SCREEN_TYPES` and accessibility docs; example fixtures; visual harness coverage. New scored modes also need SCORM interaction-type mapping and objective tests.
- **Protected surfaces:** scoring, navigation, suspend encoding, and package output are maintainer-reviewed changes under [`AGENTS.md`](../AGENTS.md). Keep new pure logic in focused modules and load optional runtime pieces only when needed. Do not edit vendored runtime, weaken sanitization/SSRF, or rewrite `AGENTS.md` to bypass these rules.
- **Compatibility proof:** keep flat/untimed/unrelated packages byte-identical wherever the feature is opt-in. Any intentionally global correctness fix needs explicit scope and reviewed golden/visual baseline changes, not blanket regeneration to make tests green.
- **State budgets:** account for question draws, responses, attempts, hub return context, and cue state within the existing 3,500-byte SCORM 1.2 working budget. Define safe recovery priorities before changing the serializer; critical attempt restrictions must not silently vanish when optional state is trimmed.
- **Test layers:** Pydantic/validator/render tests; in-memory MCP create/add/update/build calls; pure JS state tests; real Playwright timing/navigation/a11y tests; fake-LMS SCORM 1.2/2004 probes; offline ZIP/manifest checks; pinned-container visual regression. Accessibility CI is currently advisory, so critical new accessibility behavior needs explicit acceptance tests.
- **Asset policy:** packaged imagery, narration, fonts, and resource files need allowed-source provenance; keep large models and generated media out of Git. No runtime dependency on external design assets/CDNs for new native components.

### Distribution housekeeping: separate decision

The README badges, official-source table, container instructions, skill link, and `server.json` still name the upstream `kemalyy` distribution. This is expected provenance for an upstream fork, but misleading if presented as an independently supported product.

Choose either **an explicitly documented upstream-derived fork** or **your own distribution with real owned endpoints/registry identifiers**. Preserve MIT attribution and third-party notices; do not invent replacement domains or imply ownership of upstream services. Audit security/reporting links and translated READMEs consistently. Do this separately from runtime feature work. Existing Turkish developer comments need not be mass-translated to deliver English/Arabic learner experiences.

## 6. Verification performed

| Check on the unchanged baseline | Result |
|---|---|
| `.venv/bin/python -m pytest -q -ra` | **952 passed, 12 skipped** |
| `npm test` | **307 passed**, 16 test files |
| `.venv/bin/ruff check .` with CI-pinned **Ruff 0.15.16** | **Clean** |
| `node tests/test_timeline_cues.mjs` | Passed; tests the copied distribution function only |
| Model/render probes | Confirmed 31 screen types; no proposed native screen types/cue field; content-block reveal grouping; existing `tts_voice`; no persisted project voice; Arabic UI fallback |
| Isolated execution of actual timeline code | Confirmed the 8-second/3-unit early-completion case, missing entry-time Next lock, and reveal-disabled audio binding behavior described above |
| PR #1 read-only inspection | Open at the head recorded above; no approval checks added to build/TTS paths; estimated cues only |

The Python skips were **10 offline XSD checks, 1 check requiring an external pedagogy source directory, and 1 ffmpeg-dependent test**. Browser/LMS probes, pinned-container visual comparison, real voice synthesis, and forced alignment were **not run** here; browser/model/container prerequisites were not provisioned. Passing the local suites is not evidence that those skipped layers pass.

An initial run with unpinned Ruff 0.17.0 reported 269 findings; the repository's CI version, pinned in `.github/workflows/ci.yml`, reported none. The pasted “271 existing lint errors” and “967 tests” are not the measured baseline for this checkout.

**Changes made by this audit:** this planning document only. No application code, tests, fixtures, dependencies, README branding, GitHub issues, or PR state were changed.
