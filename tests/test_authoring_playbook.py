"""Tam yazarlık şablonu, kapılar, video yönlendirme ve MCP sözleşmesi."""
import json
from pathlib import Path

import pytest

from core.authoring import lint_authoring_plan, video_workflow
from core.project import AuthoringPlan

ROOT = Path(__file__).resolve().parent.parent


def example():
    return json.loads((ROOT / "playbook/templates/authoring-plan.example.json").read_text())


def codes(data, stage="planning"):
    return {i["code"] for i in lint_authoring_plan(AuthoringPlan.model_validate(data), stage)["issues"]}


def approved():
    data = example()
    for review in data["reviews"]:
        review.update(status="approved", reviewer="Client reviewer",
                      evidence="Explicit approval of revision 1 recorded in client conversation.")
    for video in data["videos"]:
        video.update(license_review="confirmed", license_note="Reviewed applicable engine terms.")
    return data


def delivered():
    data = approved()
    for asset in data["assets"]:
        asset.update(status="registered", registered_asset_id="asset_" + asset["id"])
    for check in data["quality_checks"]:
        check.update(status="passed", evidence="Illustrative test evidence; replace with real results.")
    return data


def test_planning_example_clean_and_deterministic():
    plan = AuthoringPlan.model_validate(example())
    report = lint_authoring_plan(plan)
    assert report["clean"]
    assert report == lint_authoring_plan(plan)
    assert report["approval_verification"] == "self_reported_not_authenticated"
    assert report["build_enforcement"] is False


def test_production_requires_reviews_and_license():
    assert {"approval_missing", "video_license_pending"} <= codes(example(), "production")
    assert lint_authoring_plan(AuthoringPlan.model_validate(approved()), "production")["clean"]


def test_delivery_requires_registration_and_qa():
    assert {"asset_not_registered", "qa_incomplete"} <= codes(approved(), "delivery")
    assert lint_authoring_plan(AuthoringPlan.model_validate(delivered()), "delivery")["clean"]


@pytest.mark.parametrize("section", ["sources", "objectives", "assets", "characters",
                                     "activities", "videos", "reviews", "quality_checks"])
def test_duplicate_ids(section):
    data = example()
    data[section].append(dict(data[section][0]))
    assert "duplicate_id" in codes(data)


@pytest.mark.parametrize("section,field", [("objectives", "source_ids"),
                                          ("objectives", "assessment_screen_ids"),
                                          ("assets", "screen_ids"),
                                          ("activities", "objective_ids"),
                                          ("activities", "asset_ids")])
def test_unknown_references(section, field):
    data = example()
    data[section][0][field] = ["missing"]
    assert "unknown_reference" in codes(data)


def test_assets_character_escape_and_rights_errors():
    data = example()
    data["assets"][0]["alt_text"] = None
    data["assets"][1]["variant"] = "wrong"
    data["assets"][3]["transcript"] = None
    data["activities"][0]["solution"] = None
    data["sources"][0]["reuse"] = "authorized_assets"
    assert {"missing_alt_text", "missing_character_variant", "missing_transcript",
            "incomplete_escape_room", "reference_rights_unresolved"} <= codes(data)


def test_video_limits_and_caption_kind():
    data = example()
    data["videos"][0]["shots"][0]["duration_sec"] = 61
    data["videos"][0]["captions_asset_id"] = "note"
    assert {"unsupported_video_route", "wrong_asset_kind"} <= codes(data)
    data["videos"][0]["captions_asset_id"] = None
    assert "video_captions_missing" in codes(data)
    data["videos"][0].update(engine="remotion", execution="existing_server")
    assert "unsupported_video_route" in codes(data)


def test_module_and_language_mismatch():
    data = example()
    data["visual_plan"]["module_id"] = "different"
    data["narration_script"]["language"] = "ar"
    assert "module_mismatch" in codes(data)


@pytest.mark.parametrize("value", [-1, 0, float("inf"), float("nan")])
def test_nonfinite_or_zero_video_duration_rejected(value):
    data = example()
    data["videos"][0]["shots"][0]["duration_sec"] = value
    with pytest.raises(ValueError):
        AuthoringPlan.model_validate(data)


def test_routing_defaults_and_explicit_preference():
    assert video_workflow()["engine"] == "hyperframes"
    assert video_workflow(needs_react=True)["engine"] == "remotion"
    assert video_workflow("hyperframes", True)["engine"] == "hyperframes"
    route = video_workflow("remotion")
    assert route["server_tools"] == []
    assert route["installed_verified"] is False
    assert route["license_review_required"] is True
    with pytest.raises(ValueError):
        video_workflow("bogus")
    with pytest.raises(ValueError):
        lint_authoring_plan(AuthoringPlan.model_validate(example()), "bogus")


@pytest.mark.asyncio
async def test_mcp_complete_workflow_and_video_prompts():
    from fastmcp import Client
    from fastmcp.exceptions import ToolError

    import server

    async with Client(server.mcp) as client:
        assert "get_playbook('overview')" in client.initialize_result.instructions
        assert "get_video_workflow" in client.initialize_result.instructions
        for topic in ["overview", "reference", "assets", "characters", "games", "video",
                      "quality", "authoring"]:
            page = (await client.call_tool("get_playbook", {"topic": topic})).data
            assert page["markdown"]
        report = (await client.call_tool("lint_authoring_plan", {"plan": example()})).data
        assert report["clean"] and report["build_enforcement"] is False
        route = (await client.call_tool("get_video_workflow", {"needs_react": True})).data
        assert route["engine"] == "remotion"
        for name, args in [("author_course_from_reference", {"brief": "Receiving"}),
                           ("plan_course_video", {"brief": "Document check"})]:
            prompt = await client.get_prompt(name, args)
            assert "HyperFrames" in prompt.messages[0].content.text
            assert "Remotion" in prompt.messages[0].content.text
        for name, args in [("get_video_workflow", {"engine": "bogus"}),
                           ("lint_authoring_plan", {"plan": {}}),
                           ("lint_authoring_plan", {"plan": example(), "stage": "bogus"})]:
            with pytest.raises(ToolError):
                await client.call_tool(name, args)


def test_all_playbook_pages_present_and_wheel_inclusion_declared():
    import server

    for topic, filename in server._PLAYBOOK_PAGES.items():
        assert (ROOT / "playbook" / filename).is_file(), topic
    assert '"playbook" = "playbook"' in (ROOT / "pyproject.toml").read_text()


def test_character_master_and_missing_activity_asset_coverage():
    data = example()
    data["characters"][0]["reference_asset_id"] = "note"
    data["activities"] = []
    data["visual_plan"]["screens"][0]["imagery"] = [
        {"kind": "photo", "description": "Inspection desk", "alt_text": "Inspection desk"}]
    data["assets"] = [a for a in data["assets"] if "intro" not in a["screen_ids"]]
    assert {"wrong_character_reference", "missing_activity_plan", "missing_asset_plan"} <= codes(data)


def test_export_ssml_escapes_attributes_and_does_not_replace_markup():
    from xml.etree import ElementTree

    from core.playbook import export_audio_script
    from core.project import NarrationScript

    script = NarrationScript(module_id="m", language='en" test="bad',
                             lexicon={"name": 'say "name" & more', "SAP": 'ess "ay" pee'},
                             segments=[{"screen_id": "s", "narration":
                                        '[[cue:name]] name SAP <test> [[pause:1]]'}])
    out = export_audio_script(script)["segments"][0]
    root = ElementTree.fromstring(out["ssml"])
    assert root.find("mark").attrib == {"name": "name"}
    assert root.find("sub").attrib == {"alias": 'say "name" & more'}
    assert root.attrib == {"{http://www.w3.org/XML/1998/namespace}lang": 'en" test="bad'}
    assert out["timing_source"] == "estimated_word_count"


def test_narration_cue_rejected_when_plan_has_no_targets():
    from core.playbook import lint_narration_script
    from core.project import NarrationScript, VisualPlan

    data = example()
    data["narration_script"]["segments"][0]["narration"] = "[[cue:missing]] Check the note."
    report = lint_narration_script(NarrationScript.model_validate(data["narration_script"]),
                                   VisualPlan.model_validate(data["visual_plan"]))
    assert "unknown_cue_target" in {i["code"] for i in report["issues"]}
