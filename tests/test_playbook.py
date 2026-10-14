"""tests/test_playbook.py — ajan oyun kitabı: marka kiti → tema, görsel plan ve seslendirme
kapıları, ses metni dışa aktarımı, MCP tool/prompt yüzeyi."""

import json
from pathlib import Path

import pytest

from core.playbook import (
    brand_to_theme,
    export_audio_script,
    lint_narration_script,
    lint_visual_plan,
)
from core.project import BrandKit, NarrationScript, ThemeTokens, VisualPlan
from core.theme_dark import _contrast

TPL = Path(__file__).resolve().parent.parent / "playbook" / "templates"


def _load(name):
    return json.loads((TPL / name).read_text(encoding="utf-8"))


@pytest.fixture
def brand():
    return BrandKit.model_validate(_load("brand-kit.example.json"))


@pytest.fixture
def plan():
    return VisualPlan.model_validate(_load("visual-plan.example.json"))


@pytest.fixture
def script():
    return NarrationScript.model_validate(_load("narration-script.example.json"))


def _codes(rep):
    return {i["code"] for i in rep["issues"]}


# --- örnek şablonlar temiz olmalı (belgeler = sözleşme) ------------------------------------
def test_examples_are_clean(brand, plan, script):
    assert brand_to_theme(brand)["clean"]
    assert lint_visual_plan(plan, brand)["clean"]
    assert lint_narration_script(script, plan)["clean"]


# --- marka kiti → tema ----------------------------------------------------------------------
def test_brand_to_theme_tokens_validate_as_theme(brand):
    rep = brand_to_theme(brand)
    theme = ThemeTokens.model_validate(rep["theme_tokens"])
    assert theme.color.primary == "#123c7a"
    assert theme.color.text == "#1b2430"
    assert "Montserrat" in theme.typography.font_heading
    assert rep["roles"]["on_primary"] == "#ffffff"


def test_brand_light_primary_is_darkened_and_reported():
    b = BrandKit(name="Sunny", colors={"primary": "#ffd84d", "light": "#ffffff"})
    rep = brand_to_theme(b)
    assert rep["adjustments"] and rep["adjustments"][0]["from"] == "#ffd84d"
    new = rep["theme_tokens"]["color"]["primary"]
    assert _contrast(new, "#ffffff") >= 3.0


def test_brand_low_text_contrast_is_error():
    b = BrandKit(name="Grey", colors={"primary": "#123c7a", "dark": "#9a9a9a", "light": "#ffffff"})
    rep = brand_to_theme(b)
    assert rep["error_count"] >= 1 and "low_contrast" in _codes(rep)


def test_brand_color_must_be_hex():
    with pytest.raises(ValueError):
        BrandKit(name="X", colors={"primary": "navy"})


# --- görsel plan ----------------------------------------------------------------------------
def test_plan_missing_alt_and_duplicate_id(plan, brand):
    data = plan.model_dump(mode="json")
    data["screens"][1]["imagery"][0]["alt_text"] = None
    data["screens"][2]["screen_id"] = "s01"
    rep = lint_visual_plan(VisualPlan.model_validate(data), brand)
    assert {"missing_alt_text", "duplicate_screen_id"} <= _codes(rep)
    assert rep["error_count"] >= 2


def test_plan_low_contrast_role_pair(plan, brand):
    data = plan.model_dump(mode="json")
    data["screens"][2]["text_role"] = "secondary"
    data["screens"][2]["background_role"] = "primary"
    rep = lint_visual_plan(VisualPlan.model_validate(data), brand)
    assert "low_contrast" in _codes(rep)


def test_plan_flow_warnings():
    screens = [
        {"screen_id": f"c{i}", "screen_type": "content_slide", "purpose": "p",
         "visual_concept": "short", "background_role": "accent",
         "on_screen_text": "word " * 50}
        for i in range(5)
    ]
    rep = lint_visual_plan(VisualPlan(module_id="m", module_title="M", screens=screens))
    codes = _codes(rep)
    assert {"monotony", "passive_stretch", "no_knowledge_check", "accent_overuse",
            "text_heavy_screen", "vague_visual_concept"} <= codes
    assert rep["error_count"] == 0  # yalnız uyarılar


# --- seslendirme ----------------------------------------------------------------------------
def test_narration_flags(plan):
    s = NarrationScript.model_validate({
        "module_id": "m02-inbound",
        "segments": [
            {"screen_id": "s03",
             "narration": "As you can see on the screen, [[cue:nope]] post it in EWM now."},
            {"screen_id": "zz", "narration": "Hello there."},
            {"screen_id": "s02",
             "narration": " ".join(["word"] * 30) + ". " + "more " * 140,
             "target_sec": 10},
        ],
    })
    rep = lint_narration_script(s, plan)
    codes = _codes(rep)
    assert {"screen_talk", "unknown_cue_target", "pronunciation_missing", "unknown_screen",
            "long_sentence", "segment_too_long", "over_target_time",
            "missing_narration"} <= codes
    assert rep["error_count"] >= 2


def test_narration_redundancy():
    text = ("Check the goods against the delivery note then offload them to bulk storage and "
            "sign the note for the driver before posting")
    s = NarrationScript(module_id="m", segments=[
        {"screen_id": "a", "narration": text + ".", "on_screen_text": text}])
    assert "redundant_on_screen_text" in _codes(lint_narration_script(s))


def test_language_pace_defaults():
    seg = [{"screen_id": "a", "narration": " ".join(["w"] * 120)}]
    en = lint_narration_script(NarrationScript(module_id="m", language="en", segments=seg))
    ar = lint_narration_script(NarrationScript(module_id="m", language="ar", segments=seg))
    assert en["wpm"] == 140 and ar["wpm"] == 120
    assert ar["total_est_sec"] > en["total_est_sec"]


def test_export_audio_script(script):
    out = export_audio_script(script)
    s03 = next(x for x in out["segments"] if x["screen_id"] == "s03")
    assert "[[" not in s03["tts_text"] and "[[" not in s03["narration_text"]
    assert "mee-go" in s03["tts_text"] and "MIGO" in s03["narration_text"]
    assert '<sub alias="mee-go">MIGO</sub>' in s03["ssml"]
    assert '<mark name="check"/>' in s03["ssml"]
    assert s03["filename"] == "m02-inbound_s03.mp3"
    times = [c["at_sec"] for c in s03["cues"]]
    assert [c["cue"] for c in s03["cues"]] == ["check", "offload", "sign", "post"]
    assert times == sorted(times) and times[0] > 0
    s01 = next(x for x in out["segments"] if x["screen_id"] == "s01")
    assert '<break time="0.5s"/>' in s01["ssml"]
    assert "| s03 |" in out["voice_talent_md"] and "**MIGO** → mee-go" in out["voice_talent_md"]


def test_export_is_deterministic(script):
    assert export_audio_script(script) == export_audio_script(script)


# --- MCP yüzeyi -----------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_mcp_tools_and_prompts():
    from fastmcp import Client

    import server

    async with Client(server.mcp) as c:
        names = {t.name for t in await c.list_tools()}
        assert {"get_playbook", "brand_to_theme", "lint_visual_plan", "lint_narration_script",
                "export_audio_script"} <= names
        prompts = {p.name for p in await c.list_prompts()}
        assert {"plan_module_visuals", "write_module_narration"} <= prompts

        pb = (await c.call_tool("get_playbook", {"topic": "visual"})).data
        assert "Module visual plan" in pb["markdown"] and pb["template_json"]

        brand = _load("brand-kit.example.json")
        plan = _load("visual-plan.example.json")
        script = _load("narration-script.example.json")
        th = (await c.call_tool("brand_to_theme", {"brand": brand})).data
        assert th["clean"] and th["theme_tokens"]["color"]["primary"] == "#123c7a"

        # tema set_theme'e aynen verilebilmeli
        pid = (await c.call_tool("create_project", {"title": "T"})).data.project_id
        await c.call_tool("set_theme", {"project_id": pid, "theme_tokens": th["theme_tokens"]})

        lv = (await c.call_tool("lint_visual_plan", {"plan": plan, "brand": brand})).data
        assert lv["clean"]
        ln = (await c.call_tool("lint_narration_script",
                                {"script": script, "plan": plan})).data
        assert ln["clean"] and ln["total_est_sec"] > 0
        ex = (await c.call_tool("export_audio_script", {"script": script})).data
        assert len(ex["segments"]) == 4

        pr = await c.get_prompt("plan_module_visuals", {"module_title": "Inbound"})
        text = pr.messages[0].content.text
        assert "Inbound" in text and "lint_visual_plan" in text

        from fastmcp.exceptions import ToolError

        with pytest.raises(ToolError):
            await c.call_tool("get_playbook", {"topic": "nope"})
