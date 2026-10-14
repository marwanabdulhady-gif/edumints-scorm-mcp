# 1 · Brand kit

**Goal:** capture the client's visual and verbal identity once, as data, so every module looks
and sounds like the same company.

Template: [`templates/brand-kit.example.json`](templates/brand-kit.example.json) ·
Gate: `brand_to_theme(brand)` → `set_theme(project_id, theme_tokens)`

## Where to get the brand

Use the best source available, in this order:

1. The client's brand guidelines PDF (exact hex values, typefaces, logo rules).
2. Existing approved materials: previous courses, slide templates, the website.
3. The logo file — sample its dominant colours.
4. Ask the user. **Never invent brand colours.** If you had to guess, say so and ask for
   confirmation before building.

## Fields

| Field | What to put | Notes |
|---|---|---|
| `colors.primary` | The main brand colour | Headers, buttons, title backgrounds |
| `colors.secondary` | Second brand colour | Icon tiles, highlights, links |
| `colors.accent` | Attention colour | Use sparingly: exceptions, warnings, key numbers |
| `colors.dark` | Body text colour | Usually a near-black or dark navy, not pure #000 |
| `colors.light` | Page background | Usually an off-white |
| `colors.surface` | Card background | Usually white |
| `colors.success/error/warning` | Only if the brand defines them | Otherwise safe defaults are used |
| `fonts.heading/body` | Font family names | If the font file is available, add it as an asset + `custom_fonts` |
| `imagery_style` | One or two sentences | Photo vs illustration, overlays, icon style, what to avoid |
| `voice.tone`, `voice.persona`, `voice.formality` | How the narrator sounds | Feeds the narration script |
| `do` / `dont` | Short, concrete rules | Copy these from the guidelines when they exist |

All colours are `#RRGGBB`.

## Colour roles (used by the visual plan)

The visual plan never uses hex values; it uses **roles**:
`primary`, `secondary`, `accent`, `dark`, `light`, `surface`, `success`, `error`, `warning`,
and `on_primary` (white or near-black, whichever reads better on `primary`).

Apply the **60-30-10 rule** per module:

- ~60% neutral (`light`/`surface` backgrounds, `dark` text)
- ~30% brand (`primary`/`secondary`: headers, tiles, title screens)
- ~10% `accent` (only what must jump out)

## Running the gate

```
result = brand_to_theme(brand)
```

- `result.contrast` lists every pair checked (text on background, button label on primary, …).
- If `primary` is too light to read against the page background (below 3:1), the server derives
  the closest darker variant and lists it in `result.adjustments`. **Tell the user** — this is a
  visible change to their brand.
- A text/background pair below 4.5:1 is an `error`. Don't build; propose a darker text colour or
  lighter background and ask.
- When clean, call `set_theme(project_id, result.theme_tokens)`. Combine with a style preset
  (`list_themes`) if the user wants a particular feel (`style-minimal`, `style-premium`, …).

## Arabic / bilingual brands

- Set `language: "ar"`. The player switches to right-to-left automatically.
- Pick fonts with full Arabic coverage (e.g. Tajawal, Cairo, IBM Plex Sans Arabic, Dubai).
  Latin-only brand fonts break Arabic text — use the brand font for Latin and an approved Arabic
  pair for Arabic, and record both in `do`.
