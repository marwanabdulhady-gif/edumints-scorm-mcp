# 4 · Audio production

**Goal:** turn the approved script into one audio file per segment, attach it to the right
screen, and keep captions in sync.

Gate/helper: `export_audio_script(script)`

## What `export_audio_script` gives you

For every segment:

| Field | Use it for |
|---|---|
| `tts_text` | Plain text for TTS — markup removed, lexicon pronunciations applied |
| `ssml` | The same with `<break>`, `<mark>` (cues) and `<sub alias>` — for SSML-capable engines |
| `narration_text` | Captions/transcript — original spelling, no markup. Goes into the screen's `narration_text` |
| `filename` | `<module_id>_<screen_id>[_<part>].mp3` — use it as-is |
| `est_sec` | Expected duration — compare with the real file |
| `cues` | Estimated `at_sec` for each `[[cue:id]]` |

Plus `voice_talent_md`: a ready-to-send script for a human voice actor.

## Choose a voice route

| Route | When | How |
|---|---|---|
| **Server TTS (Piper)** | Drafts, internal pilots, languages with an installed voice | `synthesize_speech(project_id, tts_text, voice, filename)` → returns the asset |
| **External TTS** (your own TTS MCP or service) | Client-facing English/Arabic with a premium voice | Send `ssml` (or `tts_text`), then `add_asset(project_id, <audio url or data URI>, filename)` |
| **Human voice talent** | Flagship or customer-facing courses | Send `voice_talent_md`; on delivery, upload each file with `add_asset` |

Whatever the route, run `normalize_audio_asset` so every file has the same loudness.

## Attach audio to screens

For each segment, update the screen in the spec:

```json
{
  "id": "s03",
  "narration_asset_id": "<asset id returned by synthesize_speech/add_asset>",
  "narration_text": "<narration_text from export_audio_script>",
  "lock_until_complete": true,
  "reveal": "auto"
}
```

- `narration_text` provides captions and the transcript (accessibility) — never leave it out.
- `lock_until_complete: true` keeps **Next** disabled until the audio finishes. Leave it
  `false` on question screens and on menu/hub screens.
- Screen elements are revealed across the audio's duration in order. Put the blocks in the
  same order as the cues in the narration so they appear when the narrator mentions them.

## Quality check before build

- [ ] Every narrated plan screen has an audio file and `narration_text`
- [ ] Real durations are within ±15% of `est_sec` (if not, the pace is off — adjust `wpm` and
      re-run the lint so time budgets stay honest)
- [ ] Spot-listen to the first, a middle and the last file: pronunciation of lexicon terms,
      no clipped endings, consistent volume
- [ ] `lint_course` reports no `narration_without_transcript`
