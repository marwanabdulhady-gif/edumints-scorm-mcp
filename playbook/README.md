# Authoring Agent Playbook

**Start here when the user asks for an e-learning course, module, game, escape room,
character pack, or course video—especially when they supply a sample course.**

Audience: any AI author connected to the MCP server. Coding contributors still read
`AGENTS.md`; this playbook does not replace those repository rules.

The AI client analyzes, designs and orchestrates creation. This server validates, renders
supported screens and packages SCORM. The user approves creative and production decisions.
The server never calls an LLM or an image-generation model.

## Discovery and production sequence

1. Call `get_playbook('overview')`, `list_screen_types`, and `list_themes`. Confirm accessible
   source files, audience, objectives, language, module length and desired deliverables.
2. Read `reference`: inspect sample course and source evidence. Separate observed facts,
   design patterns, assumptions, and client-approved asset reuse. Never invent an inspection.
3. Read `brand`, `visual`, and `authoring`: create the brand kit and complete screen-by-screen
   production plan. Source facts become objectives, narrative and assessed evidence—not a
   slide-for-slide copy of the sample.
4. Read `assets`, `characters`, and `games` when relevant. Plan all visuals, character variants,
   game objects, scenarios, clues, hints, feedback, scoring, and accessible alternatives.
5. Read `narration` and `audio`: write scripts, lexicon, cue intentions, captions/transcripts,
   voice brief, and audio-production handoff. Narration should explain, not read the screen.
6. **If video is requested:** call `get_video_workflow`, read `video`, then consult the selected
   HyperFrames or Remotion repository instructions. Plan shots before rendering.
7. Run `brand_to_theme`, `lint_visual_plan`, `lint_narration_script`, and
   `lint_authoring_plan(plan, stage='planning')`. Resolve errors and document warning decisions.
8. **STOP for explicit user approval** of visuals, characters, interaction design, narration,
   and video storyboard/license route where relevant. Show useful tables, not just raw JSON.
   Record approval evidence for the current revision; changes invalidate affected approvals.
9. Run the production-stage lint. Use available client tools or human/client-provided media.
   Produce, inspect, register assets, and map planning IDs to returned server asset IDs.
10. Assemble supported screens, lint the course, preview, revise, run delivery-stage lint,
    build/validate the package, and present the requested deliverables with honest QA evidence.

## Topic catalogue

| `get_playbook` topic | Instructions | Structured example |
|---|---|---|
| `brand` | [Brand kit](01-brand-kit.md) | `brand-kit.example.json` |
| `visual` | [Module visual plan](02-visual-plan.md) | `visual-plan.example.json` |
| `narration` | [Narration](03-narration-script.md) | `narration-script.example.json` |
| `audio` | [Audio production](04-audio-production.md) | — |
| `reference` | [Reference analysis](05-reference-analysis.md) | — |
| `assets` | [Asset production](06-asset-production.md) | — |
| `characters` | [Character consistency](07-character-design.md) | — |
| `games` | [Gamification and escape rooms](08-games-and-escape-rooms.md) | — |
| `video` | [HyperFrames / Remotion](09-video-production.md) | complete plan |
| `quality` | [QA and delivery](10-quality-and-delivery.md) | — |
| `authoring` | [Complete planning contract](11-complete-authoring.md) | `authoring-plan.example.json` |

Examples are under `playbook/templates/`. Load the full workflow with the
`author_course_from_reference` MCP prompt; use `plan_course_video` for video requests.

## Honest guarantees

These tools deterministically check documents **when called**. They do not force a client to
load a prompt, authenticate human approval, persist plans, generate assets, or gate the existing
TTS/build entry points. Approval records are self-reported review evidence, not authorization.
Calling a production lint is not itself permission to generate media. An agent must wait for
an actual user response. Do not label planning timestamps as measured audio alignment.

Do not promise unimplemented canvas/process-flow/hub/final-exam features. Use discovery and the
existing screen schemas, or explicitly offer a supported fallback and seek approval. No unseen
sample assets, unsupported integrations, or skipped QA may be described as completed work.
