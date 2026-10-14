# 3 · Narration script

**Goal:** a voice-over script, one segment per screen (or per screen part), that explains what
the screen only shows — timed, pronounceable and synced to the visual plan.

Template: [`templates/narration-script.example.json`](templates/narration-script.example.json) ·
Gate: `lint_narration_script(script, plan)`

## Writing rules

1. **Write for the ear.** Short sentences (max 25 words), one idea per sentence, contractions
   ("you'll", "don't"). Read it aloud in your head: if you'd run out of breath, split it.
2. **Talk to one person.** "You", present tense, active voice. Use the brand's `voice.persona`
   and `voice.tone` — e.g. a supervisor coaching a new colleague, not a textbook.
3. **Complement the screen; don't read it.** The screen holds keywords; the narration explains
   them (Mayer's redundancy principle). The gate flags narration that repeats the on-screen text
   word for word.
4. **Narrate the idea, not the interface.** No "as you can see on this slide" or "click next to
   continue" — the player already handles navigation.
5. **Open with why, close with what's next.** First screen of a module: why this matters on the
   job. Last screen: what the learner can now do.
6. **Scenarios and questions:** set up the situation and stop. Never narrate the answer on a
   question screen. Feedback text goes in the screen's `feedback`, not the narration.
7. **Respect the time budget.** About 140 words/minute in English, 120 in Arabic, 130 in Turkish.
   Keep each segment under 60 seconds; if it's longer, split it across screen parts (tabs,
   hotspot regions) or another screen.

## Markup

| Markup | Meaning |
|---|---|
| `[[cue:id]]` | Reveal the plan element `id` at this moment (must be in the screen's `cue_targets`) |
| `[[pause:1.0]]` | Silence, in seconds (rendered as SSML `<break>` for TTS) |

Markup is stripped from captions and transcripts automatically.

## Segment fields

| Field | Required | Notes |
|---|---|---|
| `screen_id` | yes | Must exist in the visual plan |
| `narration` | yes | The spoken text, with markup |
| `on_screen_text` | recommended | Copy from the plan — lets the gate check redundancy |
| `target_sec` | recommended | Your time budget for this segment |
| `tone` | optional | Direction for TTS / voice talent ("curious", "serious", "upbeat") |
| `part` | optional | Sub-part id: a hotspot region, tab or layer with its own audio |

## Pronunciation lexicon

Every acronym and product term goes in `lexicon` with how it should be spoken:
`"SAP": "S-A-P"`, `"MIGO": "mee-go"`, `"EWM": "E-W-M"`. The gate warns about any
all-caps term without an entry. The lexicon is applied to the TTS text and turned into SSML
`<sub alias>`, so captions still show the correct spelling.

## Gate codes

| Code | Severity | Meaning |
|---|---|---|
| `empty_narration` | error | Segment has no spoken text |
| `unknown_screen` | error | `screen_id` not in the visual plan |
| `unknown_cue_target` | error | `[[cue:x]]` not in that screen's `cue_targets` |
| `segment_too_long` | warn | Over 60 seconds |
| `over_target_time` | warn | Over `target_sec` by more than 15% |
| `long_sentence` | warn | Sentence over 25 words |
| `screen_talk` | warn | Talks about the interface instead of the content |
| `pronunciation_missing` | warn | Acronym without a lexicon entry |
| `redundant_on_screen_text` | warn | Narration reads the screen word for word |
| `missing_narration` | warn | A plan screen (other than a quiz question) has no segment |

The report also returns `total_est_min` — compare it with the module's seat-time budget.

## Arabic narration

- Use Modern Standard Arabic unless the client asks for a dialect; keep a friendly register
  (`formality: conversational` still applies).
- Keep English system terms (SAP transaction codes, form names) in Latin script inside the
  Arabic text, and give each a lexicon entry so TTS pronounces it correctly.
- Write numbers as digits on screen; in narration, spell out anything the TTS might misread.
- The default pace is 120 wpm — set `wpm` explicitly if your voice is faster or slower.

## Presenting the script to the user

Run `export_audio_script(script)` and show `voice_talent_md` — a table with screen, tone,
script and estimated seconds, plus the pronunciation guide. Get explicit approval before
recording or synthesising audio.
