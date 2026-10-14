# Video production: HyperFrames or Remotion

**For any request to create/edit/render a video**, call `get_video_workflow` and read this page.
Select an engine, inspect its upstream README/agent instructions for a pinned version, and use
it in an approved workspace. A link is guidance—not an installed integration.

## Engine decision

| Engine | Choose when | Integration here |
|---|---|---|
| [HyperFrames](https://github.com/heygen-com/hyperframes) | HTML/CSS animated explainers, diagrams, course-screen motion; default when no React requirement | Existing optional `render_motion_video` / `render_screen_video`; otherwise client workspace |
| [Remotion](https://github.com/remotion-dev/remotion) | React composition, reusable components, data-driven scenes, or an existing Remotion project | Client workspace only; import exported MP4 via `add_asset` |

Respect an explicit user preference. `auto` recommends HyperFrames unless `needs_react=true`.
Neither framework supplies the course's writing, voice, imagery or legal permissions. Do not
confuse HyperFrames with a HeyGen hosted avatar/voice service. Do not duplicate a complete engine
repository inside this repo. Use optional dependencies or separate client projects.

## Upstream instructions and licensing

Sources inspected 2026-10-14: each linked repository README and license. Recheck the chosen
release before installation; APIs/skills/license terms change. HyperFrames currently declares
Apache-2.0 and agent skills in its README. Read its router/creation workflow instructions for
explainer or general-video work. Remotion's README describes React-based video and agent skills;
its [LICENSE.md](https://github.com/remotion-dev/remotion/blob/main/LICENSE.md) is **not MIT** and
includes Free/Company License eligibility. Confirm the applicable terms with the user before
commercial use. No dependency is relicensed by our MIT license.

Upstream discovery examples (not commands executed automatically by the MCP server):
- HyperFrames README: `npx skills add heygen-com/hyperframes` for skills; consult its current
  non-interactive installation instructions when working as an agent.
- Remotion README: `npx create-video@latest` to scaffold. After discovery, pin package versions
  and lockfiles rather than using an unbounded latest version for reproducible production.

Ask before installations, external uploads, paid renders or credential-dependent services.
Never put provider keys in chat, source files or the course package. Check local Node/browser,
ffmpeg, network, fonts and engine availability; report missing prerequisites without claiming success.

## Plan → approve → render → package

1. Confirm purpose, audience, language, duration, aspect/resolution, brand, accessibility,
   engine preference, and whether standalone MP4 or a course screen is requested.
2. Write `VideoPlan`: engine/reason/execution, license review, output/captions asset IDs, shots
   with durations, visual actions, narration and required asset IDs. Write scripts and a lexicon.
3. Show shot table, voice sample where available, representative frame and production estimate.
   Get explicit storyboard/narration/visual approval before expensive production.
4. Generate/import approved assets with the client tools. Use local fonts/media and deterministic,
   seekable/frame-based animations per the chosen engine; no arbitrary network calls per frame.
5. Preview representative frames and complete timing, then render MP4. Inspect start/middle/end,
   narration sync, legibility, RTL, clipping, missing media, audio level and playback duration.
6. Export MP4, poster, original transcript and **real time-synced WebVTT**. Estimated narration
   cue times are not a substitute for measured captions. Preserve source project/lockfile for edits.
7. For courses: register files, attach `video_asset_id`, `poster_asset_id`, `captions_asset_id`
   and `narration_text` to a supported `video` screen. Do not add separate narration audio if
   already muxed in the MP4. Test controls/captions in preview and the packaged LMS runtime.
8. For standalone video: deliver MP4 (and requested captions/source), not a forced SCORM package.

## Existing server constraints

`render_motion_video` compiles the server's `VideoSpec`, not arbitrary React or a full upstream
HyperFrames project. Its guardrails are **1920×1080 max, 60 seconds max, 60 fps max**.
`render_screen_video` uses the existing course screen. These optional tools require rendering
prerequisites; discovery does not verify installation. Narration timing still needs inspection.
For longer videos, arbitrary compositions or Remotion, render in the client workspace and
upload outputs; don't silently change server limits or imply a native Remotion MCP tool exists.
`make_video_from_image_audio` is a simple still-image/audio fallback, not equivalent animation.
