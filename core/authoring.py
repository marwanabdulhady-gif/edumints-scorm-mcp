"""Uçtan uca yazarlık denetimi ve video rotası; model/üretim çağrısı YOK."""
from __future__ import annotations

from core.playbook import _issue, _report, lint_narration_script, lint_visual_plan
from core.project import AuthoringPlan

VIDEO_ENGINES = {
    "hyperframes": {
        "repository": "https://github.com/heygen-com/hyperframes",
        "license_url": "https://github.com/heygen-com/hyperframes/blob/main/LICENSE",
        "workflow": "HTML/CSS compositions and seekable animations",
        "server_tools": ["render_motion_video", "render_screen_video"],
        "guidance": "playbook/09-video-production.md",
    },
    "remotion": {
        "repository": "https://github.com/remotion-dev/remotion",
        "license_url": "https://github.com/remotion-dev/remotion/blob/main/LICENSE.md",
        "workflow": "React compositions, reusable components and data-driven video",
        "server_tools": [],
        "guidance": "playbook/09-video-production.md",
    },
}


def video_workflow(engine: str = "auto", needs_react: bool = False) -> dict:
    """Yetenek/env uygunluğu iddiası olmadan istemciye video rotası önerir."""
    if engine not in {"auto", *VIDEO_ENGINES}:
        raise ValueError("engine must be auto, hyperframes or remotion")
    chosen = ("remotion" if needs_react else "hyperframes") if engine == "auto" else engine
    return {
        "engine": chosen,
        **VIDEO_ENGINES[chosen],
        "installed_verified": False,
        "execution": "existing_server_or_agent_workspace" if chosen == "hyperframes"
                     else "agent_workspace",
        "license_review_required": True,
        "steps": [
            "Read get_playbook('video') and the upstream instructions for a pinned version.",
            "Approve storyboard, voice, assets and license route before production.",
            "Check local dependencies; do not assume a repository link installs an engine.",
            "Render and inspect MP4, poster, captions and original transcript.",
            "Register exported files with add_asset; attach to a video screen; validate package.",
        ],
        "limits": {
            "existing_hyperframes_server": "1920x1080 maximum, 60 seconds, 60 fps",
            "remotion": "No native MCP render tool; use an approved external agent workspace.",
        },
    }


def lint_authoring_plan(plan: AuthoringPlan, stage: str = "planning") -> dict:
    """Plan/üretim/teslim aşaması denetimi; onay kayıtları doğrulanmış insan kimliği DEĞİLDİR."""
    if stage not in {"planning", "production", "delivery"}:
        raise ValueError("stage must be planning, production or delivery")
    issues = list(lint_visual_plan(plan.visual_plan)["issues"])

    def error(code, message, path):
        issues.append(_issue("error", code, message, path))

    def indexed(items, label, key="id"):
        result = {}
        for i, item in enumerate(items):
            ident = getattr(item, key)
            if ident in result:
                error("duplicate_id", f"duplicate {label} id: {ident}", f"{label}[{i}]")
            result[ident] = item
        return result

    def refs(values, available, path):
        for value in values:
            if value not in available:
                error("unknown_reference", f"unknown reference: {value}", path)

    screens = indexed(plan.visual_plan.screens, "screens", "screen_id")
    sources = indexed(plan.sources, "sources")
    objectives = indexed(plan.objectives, "objectives")
    assets = indexed(plan.assets, "assets")
    characters = indexed(plan.characters, "characters")
    indexed(plan.activities, "activities")
    indexed(plan.videos, "videos")
    if plan.visual_plan.module_id != plan.module_id:
        error("module_mismatch", "visual plan belongs to another module", "visual_plan.module_id")
    if plan.narration_script:
        if (plan.narration_script.module_id != plan.module_id
                or plan.narration_script.language != plan.language):
            error("module_mismatch", "narration module/language differs", "narration_script")
        issues.extend(lint_narration_script(plan.narration_script, plan.visual_plan)["issues"])
    for src in plan.sources:
        if src.reuse != "patterns_only" and not src.permission_note:
            error("reference_rights_unresolved", "document permissions before copying assets",
                  f"sources.{src.id}")
        if src.reuse == "unknown":
            issues.append(_issue("warn", "patterns_only", "unknown rights: reuse patterns only",
                                 f"sources.{src.id}"))
    for obj in plan.objectives:
        refs(obj.source_ids, sources, f"objectives.{obj.id}.source_ids")
        refs(obj.assessment_screen_ids, screens, f"objectives.{obj.id}.assessment_screen_ids")
    for asset in plan.assets:
        path = f"assets.{asset.id}"
        refs(asset.screen_ids, screens, path + ".screen_ids")
        if asset.character_id:
            refs([asset.character_id], characters, path + ".character_id")
        visual = asset.kind in {"image", "background", "character", "diagram", "game_object"}
        if visual and not asset.decorative and not (asset.alt_text or "").strip():
            error("missing_alt_text", "meaningful visual asset needs alt text", path)
        if asset.kind in {"audio", "video"} and not (asset.transcript or "").strip():
            error("missing_transcript", "narrated media needs a text alternative", path)
        if asset.status == "registered" and not asset.registered_asset_id:
            error("missing_registration", "registered asset needs returned server asset ID", path)
        if stage == "delivery" and asset.status != "registered":
            error("asset_not_registered", "required asset is not registered", path)
    for screen in plan.visual_plan.screens:
        linked = [a for a in plan.assets if screen.screen_id in a.screen_ids]
        if screen.imagery and not linked:
            error("missing_asset_plan", "screen imagery needs production manifest entries",
                  f"screens.{screen.screen_id}")
        if screen.screen_type.value in {"escape_room", "game", "decision_scenario"} and not any(
            a.screen_id == screen.screen_id for a in plan.activities
        ):
            error("missing_activity_plan", "interactive game screen needs rules and evidence",
                  f"screens.{screen.screen_id}")
    for char in plan.characters:
        refs([char.reference_asset_id], assets, f"characters.{char.id}.reference_asset_id")
        master = assets.get(char.reference_asset_id)
        if master and (master.kind != "character" or master.character_id != char.id):
            error("wrong_character_reference", "master must reference this character's asset",
                  f"characters.{char.id}.reference_asset_id")
        variants = {a.variant for a in plan.assets if a.character_id == char.id}
        if not set(char.variants) <= variants:
            error("missing_character_variant", "plan an asset for every required character variant",
                  f"characters.{char.id}")
    for act in plan.activities:
        path = f"activities.{act.id}"
        refs([act.screen_id], screens, path + ".screen_id")
        refs(act.objective_ids, objectives, path + ".objective_ids")
        refs(act.evidence_source_ids, sources, path + ".evidence_source_ids")
        refs(act.asset_ids, assets, path + ".asset_ids")
        if act.kind == "escape_room" and not (act.hints and act.solution and act.debrief):
            error("incomplete_escape_room", "escape room needs hints, solution and debrief", path)
    for video in plan.videos:
        path = f"videos.{video.id}"
        refs([video.screen_id], screens, path + ".screen_id")
        refs([video.output_asset_id], assets, path + ".output_asset_id")
        output = assets.get(video.output_asset_id)
        if output and output.kind != "video":
            error("wrong_asset_kind", "video output must reference a video asset", path)
        indexed(video.shots, path + ".shots")
        for shot in video.shots:
            refs(shot.asset_ids, assets, path + f".shots.{shot.id}.asset_ids")
        if video.captions_asset_id:
            refs([video.captions_asset_id], assets, path + ".captions_asset_id")
            caption = assets.get(video.captions_asset_id)
            if caption and caption.kind != "captions":
                error("wrong_asset_kind", "caption output must be a captions asset", path)
        elif any(s.narration for s in video.shots):
            error("video_captions_missing", "narrated video needs a caption asset plan", path)
        duration = sum(s.duration_sec for s in video.shots)
        if video.execution == "existing_server" and (
            video.engine != "hyperframes" or video.width > 1920 or video.height > 1080
            or duration > 60
        ):
            error("unsupported_video_route", "existing server route is HyperFrames <=1080p/60s",
                  path)
        if stage != "planning" and (
            video.license_review != "confirmed" or not video.license_note
        ):
            error("video_license_pending", "confirm engine license before rendering", path)
    reviews = indexed(plan.reviews, "reviews", "scope")
    if stage != "planning":
        required = {"visual"}
        if plan.characters:
            required.add("characters")
        if plan.activities:
            required.add("interaction")
        if plan.narration_script or any(a.kind in {"audio", "video"} for a in plan.assets):
            required.add("narration")
        if plan.videos:
            required.add("video")
        for scope in sorted(required):
            record = reviews.get(scope)
            if not record or record.status != "approved" or not record.reviewer or not record.evidence:
                error("approval_missing", f"record approval for {scope} at revision {plan.revision}",
                      f"reviews.{scope}")
    checks = indexed(plan.quality_checks, "quality_checks", "category")
    if stage == "delivery":
        required = {"source_accuracy", "assets", "accessibility", "responsive", "scorm"}
        if plan.activities:
            required.add("branching_scoring")
        if plan.narration_script or any(a.kind in {"audio", "video"} for a in plan.assets):
            required.add("audio_sync")
        if plan.videos:
            required.add("video")
        for category in sorted(required):
            check = checks.get(category)
            if not check or check.status not in {"passed", "not_applicable"} or not check.evidence:
                error("qa_incomplete", f"record QA evidence for {category}",
                      f"quality_checks.{category}")
    return _report(issues, module_id=plan.module_id, revision=plan.revision, stage=stage,
                   approval_verification="self_reported_not_authenticated",
                   build_enforcement=False)
