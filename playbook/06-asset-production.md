# Asset manifest and production

Plan **every required asset** before generating: backgrounds, illustrations, diagrams, photos,
UI screenshots, character variants, narration, music/SFX, animations, game props, video exports,
posters, captions and resource documents. For each record stable planning ID, kind, consuming
screen IDs, production brief/route, rights/provenance, alt text or transcript, and status.

Expand `brief` with dimensions/aspect, crop/safe areas, brand roles, style, transparency, intended
layer, and acceptance criteria. Audio briefs include language/accent, approved voice, pace,
pronunciations, duration target and loudness policy. Game-object briefs specify clue relevance,
state variants and non-color-only meaning. Never generate text-heavy slides as flattened images
when real HTML text is available. Sound effects/music need a described purpose and mute policy.

Discover tools actually available to the client. Use image/design/audio tools for media; use
`svg_to_asset` for authored diagrams; upload client/human media with `add_asset`; use `piper` only
with an installed language-appropriate model. No available tool? Ask for upload, offer a clearly
labeled placeholder draft, or state the blocked task. Do not pretend to generate music with a
spoken-word TTS service or make character animation with an image-only tool.

Produce one approved representative scene/character first, review, then expand variants. Inspect
outputs for accuracy, legibility, artifacts, consistency, pronunciation and clipping. Regenerate
only affected assets. Keep generation prompts, source links, model/provider version where known,
rights and revision notes. `stock` does not mean free: accept only allowed-source provenance
(`ai-generated`, `cc0`, `public-domain`, `own`, `local`) with a truthful rights record.

Map `planned_id → returned asset_id → filename → consuming screens`. Status `registered` means
an actual server ID was returned, not a fabricated name. Attach binaries via server storage;
never leave expiring CDN links as runtime dependencies. Planning source labels are not a substitute
for package provenance. Reuse approved assets across screens instead of unnecessary regeneration.
