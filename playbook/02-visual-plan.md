# 2 · Module visual plan

**Goal:** before building anything, decide screen by screen what the learner **sees**, in the
brand's colours, and why. The plan is the storyboard; the build simply executes it.

Template: [`templates/visual-plan.example.json`](templates/visual-plan.example.json) ·
Gate: `lint_visual_plan(plan, brand)`

## Steps

1. **Start from the objective.** Write the module `objective` as one observable behaviour
   ("Receive finished goods … and post them correctly in SAP"). Every screen must serve it.
2. **Chunk the content.** One idea per screen. A process with 8 steps is not one screen —
   group it into 3–4 meaningful stages.
3. **Choose the screen type for the learning job, not for variety.** Call `list_screen_types`.
   Typical picks:

   | Learning job | Screen type |
   |---|---|
   | Introduce / set context | `title_slide`, `content_slide` (full_media) |
   | Explain a process or sequence | `content_slide` with cue-revealed blocks, `timeline`, `worked_example` |
   | Explore parts of a whole | `hotspot` (`mode: explore`, `require_all`), `tabs`, `accordion`, `labeled_diagram` |
   | Practise a decision | `decision_scenario`, `branching` |
   | Practise a system task | `simulation` (screenshots + click/type steps) |
   | Check recall / order | `mcq`, `true_false`, `matching`, `sorting`, `drag_drop` |
   | Close | `summary`, `results_breakdown` |

4. **Write the visual concept** for each screen: one or two sentences a designer could act on —
   subject, composition, what moves. Bad: "nice image of warehouse". Good: "Top-down warehouse
   map with three glowing entry points; each entry is a white icon tile."
5. **Assign colour roles** (`background_role`, `text_role`, `accent_role`) using the brand kit's
   roles and the 60-30-10 rule. Title and section-opener screens may use `primary` backgrounds
   with `on_primary` text; content screens use `light`/`surface`.
6. **List the imagery** with `kind`, `description`, `source` and `alt_text`. Mark purely
   ornamental icons `decorative: true`. Prefer the client's real photos (`client`) and generated
   SVG diagrams (`svg`) over generic stock.
7. **Write the on-screen text** — keywords only (aim for under 25 words, hard limit 45). The
   narration explains; the screen anchors.
8. **Name the cue targets.** Every element that should appear in time with the narration gets a
   short id in `cue_targets` (`check`, `offload`, …). The narration script triggers them with
   `[[cue:id]]`.

## Flow rules (checked by the gate)

| Code | Severity | Rule |
|---|---|---|
| `duplicate_screen_id` | error | Screen ids are unique — they become build ids |
| `missing_alt_text` | error | Non-decorative imagery needs `alt_text` |
| `low_contrast` | error | `text_role` on `background_role` must reach 4.5:1 |
| `role_not_in_brand` | warn | You used a role the brand doesn't define (a default will be used) |
| `vague_visual_concept` | warn | Concept under 6 words — describe what is actually seen |
| `text_heavy_screen` | warn | More than 45 on-screen words |
| `monotony` | warn | Three screens of the same type in a row |
| `passive_stretch` | warn | Five passive screens in a row — add an interaction |
| `accent_overuse` | warn | Accent used as a background on more than 10% of screens |
| `no_knowledge_check` | warn | The module never asks the learner to do anything scored |

## Presenting the plan to the user

After the gate is clean, show the plan as a table, one row per screen:
`# · screen type · purpose · visual concept · colours (bg/text/accent) · imagery source`.
Ask for approval or changes before writing the narration.

## From plan to build

| Plan field | Spec field |
|---|---|
| `screen_id` | `id` |
| `screen_type` | `type` |
| `layout` | `layout` (content_slide) |
| `animation` | `animation` |
| `imagery[].alt_text` | `image_alt` / asset alt |
| `on_screen_text` | `title` + `body_html` / `blocks` (keywords only) |

Produce imagery after approval: client photos via `add_asset`, diagrams via `svg_to_asset`,
generated images from your image tool via `add_asset`. Keep the brand's `imagery_style`.
