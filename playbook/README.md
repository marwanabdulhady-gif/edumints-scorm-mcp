# Authoring Agent Playbook

**Audience:** the AI agent (Claude, or any MCP client) that *authors* courses with this server.
This is not for coding agents working on the repo — they read [`AGENTS.md`](../AGENTS.md).

The server compiles courses; it never writes content. The quality of a course comes from the
planning the author does **before** `build_from_spec`. This playbook makes that planning
explicit and checkable. It has three planning documents, each with a deterministic gate on the
server:

| Step | Document you produce | Instructions | Server gate |
|---|---|---|---|
| 1 | **Brand kit** (once per client) | [01-brand-kit.md](01-brand-kit.md) | `brand_to_theme` |
| 2 | **Visual plan** (one per module) | [02-visual-plan.md](02-visual-plan.md) | `lint_visual_plan` |
| 3 | **Narration script** (one per module) | [03-narration-script.md](03-narration-script.md) | `lint_narration_script` |
| 4 | **Audio** (one file per screen/part) | [04-audio-production.md](04-audio-production.md) | `export_audio_script` |

Filled examples live in [`templates/`](templates/). Copy their shape exactly — the server
validates them against Pydantic models (`BrandKit`, `VisualPlan`, `NarrationScript` in
`core/project.py`).

You can read every page of this playbook at runtime with the `get_playbook` tool
(`topic`: `overview` · `brand` · `visual` · `narration` · `audio`). The server also exposes
two MCP prompts, `plan_module_visuals` and `write_module_narration`, that load these rules into
the conversation.

## The pipeline

```
Source material (SOPs, slides, SME notes, flowcharts)
        │
        ▼
1. BRAND KIT ──► brand_to_theme ──► set_theme(theme_tokens)          (once per client)
        │
        ▼  for each module:
2. VISUAL PLAN ──► lint_visual_plan(plan, brand)        fix every error, review warns
        │
        ▼
3. NARRATION SCRIPT ──► lint_narration_script(script, plan)   fix errors, review warns
        │
        ▼  ⏸ HUMAN REVIEW GATE: show plan + script table to the user, get approval
        │
        ▼
4. AUDIO ──► export_audio_script ──► synthesize_speech / external TTS / voice talent
        │                              └─► add_asset ─► narration_asset_id
        ▼
5. BUILD ──► build_from_spec (screens carry narration_text, narration_asset_id,
             lock_until_complete) ──► lint_course ──► preview ──► build_package
```

## Non-negotiable rules

1. **Never skip the gates.** Run each lint and fix every `error` before moving to the next step.
   `warn` items need a decision: fix it, or tell the user why you kept it.
2. **Stop for human review before audio.** Re-recording audio is the most expensive change in the
   pipeline. Show the user the visual plan (screen-by-screen table) and the voice-over table
   (`voice_talent_md`) and wait for an explicit "approved".
3. **One brand kit per client, reused.** Don't re-derive colours per module. If a module needs a
   different look, that is a brand decision — ask.
4. **Plan IDs are build IDs.** `screen_id` in the plan = `id` of the screen in the spec.
   `cue_targets` in the plan = the cue names used in narration. Keep them stable across revisions.
5. **Narration carries explanation; the screen carries keywords.** Never put the full script on
   screen, and never have the narrator read the screen word for word.
6. **Everything ships with text alternatives.** Every non-decorative image gets `alt_text`;
   every narrated screen gets `narration_text` (captions/transcript).

## Definition of done for a module

- [ ] `lint_visual_plan` → 0 errors
- [ ] `lint_narration_script` → 0 errors, total time within the module's budget
- [ ] User approved plan + script
- [ ] Each narrated screen has `narration_asset_id`, `narration_text`, `lock_until_complete: true`
- [ ] `lint_course` → 0 errors; `preview` checked on desktop and phone width
