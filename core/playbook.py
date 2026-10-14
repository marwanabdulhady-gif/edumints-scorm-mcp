"""Ajan oyun kitabı (playbook/) için deterministik denetim ve dönüştürücüler.

AI istemcisi (yazar) üç planlama belgesi üretir: marka kiti (BrandKit), modül görsel planı
(VisualPlan) ve seslendirme metni (NarrationScript). Bu modül bunları DETERMINISTIK olarak:

  - brand_to_theme      : marka kiti → set_theme'e verilebilir ThemeTokens + WCAG kontrast raporu
  - lint_visual_plan    : görsel plan kalite kapısı (alt-text, kontrast, monotonluk, 60-30-10 ...)
  - lint_narration_script: seslendirme kalite kapısı (süre, cümle uzunluğu, tekrar, telaffuz ...)
  - export_audio_script : TTS-hazır metin + SSML + seslendirme sanatçısı tablosu + tahmini cue zamanları

Sunucuda LLM YOK — tüm kurallar saf Python; aynı girdi her zaman aynı çıktıyı verir.
Sorun biçimi lint_course ile aynıdır: {"severity": "error"|"warn", "code", "message", "path"}.
"""
from __future__ import annotations

import re

from core.project import (
    BrandKit,
    NarrationScript,
    ScreenType,
    VisualPlan,
)
from core.theme_dark import _contrast, _mix, _to_hex

# --------------------------------------------------------------------------- #
# Sabitler
# --------------------------------------------------------------------------- #
# Dil başına varsayılan konuşma hızı (kelime/dakika). Arapça kelimeler daha uzun/bitişik
# olduğundan e-öğrenme anlatımında daha düşük hız kullanılır.
DEFAULT_WPM = {"en": 140, "ar": 120, "tr": 130}
FALLBACK_WPM = 135

MAX_SEGMENT_SEC = 60.0        # tek ekran anlatımı bunu aşarsa böl (bilişsel yük / segmentleme)
MAX_SENTENCE_WORDS = 25
MAX_ON_SCREEN_WORDS = 45
REDUNDANCY_RATIO = 0.8        # ekran metninin bu oranı anlatımda birebir geçiyorsa → tekrar kokusu
REDUNDANCY_MIN_WORDS = 15

AA_TEXT = 4.5
AA_UI = 3.0

_FONT_FALLBACK = "system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif"

SCORED_TYPES = {
    ScreenType.mcq, ScreenType.true_false, ScreenType.fill_blank, ScreenType.drag_drop,
    ScreenType.hotspot, ScreenType.matching, ScreenType.sorting, ScreenType.decision_scenario,
    ScreenType.labeled_diagram, ScreenType.adaptive_practice, ScreenType.game,
    ScreenType.term_match_race, ScreenType.escape_room, ScreenType.simulation,
}
PASSIVE_TYPES = {
    ScreenType.title_slide, ScreenType.content_slide, ScreenType.video, ScreenType.summary,
    ScreenType.lottie, ScreenType.data_chart, ScreenType.timeline,
}
ASSESSMENT_TYPES = {ScreenType.mcq, ScreenType.true_false, ScreenType.fill_blank}

_CUE_RE = re.compile(r"\[\[cue:([A-Za-z0-9_.-]+)\]\]")
_PAUSE_RE = re.compile(r"\[\[pause:(\d+(?:\.\d+)?)\]\]")
_MARK_RE = re.compile(r"\[\[[^\]]*\]\]")
_ACRONYM_RE = re.compile(r"\b[A-Z][A-Z0-9]{1,5}\b")
_WORD_RE = re.compile(r"[\w'’-]+", re.UNICODE)
_SCREEN_TALK = (
    "as you can see on the screen", "on this slide", "this slide shows", "click next to continue",
    "in this screen", "as shown on the screen",
)


def _issue(sev: str, code: str, message: str, path: str | None = None) -> dict:
    return {"severity": sev, "code": code, "message": message, "path": path}


def _report(issues: list[dict], **extra) -> dict:
    return {
        "error_count": sum(1 for i in issues if i["severity"] == "error"),
        "warn_count": sum(1 for i in issues if i["severity"] == "warn"),
        "clean": not issues,
        **extra,
        "issues": issues,
    }


def _words(text: str) -> list[str]:
    return _WORD_RE.findall(text or "")


def _darken(hex_color: str, k: float) -> str:
    return _to_hex(_mix("#000000", hex_color, k))


# --------------------------------------------------------------------------- #
# Marka kiti → tema
# --------------------------------------------------------------------------- #
def resolve_roles(brand: BrandKit) -> dict[str, str]:
    """Renk ROLÜ → hex. Tanımsız roller güvenli nötrlere düşer (görsel plan bu adları kullanır)."""
    c = brand.colors
    primary = c.primary
    on_primary = (
        "#ffffff" if _contrast("#ffffff", primary) >= _contrast("#111111", primary) else "#111111"
    )
    return {
        "primary": primary,
        "secondary": c.secondary or primary,
        "accent": c.accent or c.secondary or primary,
        "dark": c.dark or "#18181b",
        "light": c.light or "#fafafa",
        "surface": c.surface or "#ffffff",
        "success": c.success or "#168139",
        "error": c.error or "#cb2323",
        "warning": c.warning or "#975606",
        "on_primary": on_primary,
    }


def brand_to_theme(brand: BrandKit) -> dict:
    """Marka kitini set_theme'e verilebilir kısmi ThemeTokens sözlüğüne çevirir + AA raporu.

    Marka primary'si zemine karşı UI eşiğini (3:1) geçmiyorsa, en küçük koyulaştırma adımıyla
    AA-uyumlu bir varyant TÜRETİLİR ve `adjustments` içinde açıkça raporlanır (sessiz değişim yok).
    Metin/zemin çifti 4.5:1'i geçmiyorsa düzeltilmez → 'error' (marka kararı insana aittir).
    """
    roles = resolve_roles(brand)
    issues: list[dict] = []
    adjustments: list[dict] = []

    primary = roles["primary"]
    if _contrast(primary, roles["light"]) < AA_UI:
        for step in range(1, 41):
            cand = _darken(brand.colors.primary, step * 0.02)
            if _contrast(cand, roles["light"]) >= AA_UI:
                adjustments.append({
                    "role": "primary", "from": brand.colors.primary, "to": cand,
                    "reason": "primary must reach 3:1 against the page background (WCAG 1.4.11)",
                })
                primary = cand
                break
    on_primary = (
        "#ffffff" if _contrast("#ffffff", primary) >= _contrast("#111111", primary) else "#111111"
    )

    checks = [
        ("text_on_background", roles["dark"], roles["light"], AA_TEXT),
        ("text_on_surface", roles["dark"], roles["surface"], AA_TEXT),
        ("button_label_on_primary", on_primary, primary, AA_TEXT),
        ("primary_on_background", primary, roles["light"], AA_UI),
        ("accent_on_background", roles["accent"], roles["light"], AA_UI),
    ]
    contrast_report = []
    for name, fg, bg, need in checks:
        ratio = round(_contrast(fg, bg), 2)
        ok = ratio >= need
        contrast_report.append({"pair": name, "fg": fg, "bg": bg, "ratio": ratio,
                                "required": need, "pass": ok})
        if not ok:
            sev = "error" if need == AA_TEXT else "warn"
            issues.append(_issue(sev, "low_contrast",
                                 f"{name}: {ratio}:1 < {need}:1 — choose a darker/lighter pair",
                                 f"colors.{name}"))

    color = {
        "primary": primary,
        "primary_hover": _darken(primary, 0.12),
        "primary_contrast": on_primary,
        "secondary": roles["secondary"],
        "accent": roles["accent"],
        "bg": roles["light"],
        "surface": roles["surface"],
        "text": roles["dark"],
        "focus_ring": primary,
        "success": roles["success"],
        "error": roles["error"],
        "warning": roles["warning"],
    }
    tokens: dict = {"name": f"brand-{re.sub(r'[^a-z0-9]+', '-', brand.name.lower()).strip('-')}",
                    "color": color}
    typo = {}
    if brand.fonts.heading:
        typo["font_heading"] = f"'{brand.fonts.heading}', {_FONT_FALLBACK}"
    if brand.fonts.body:
        typo["font_body"] = f"'{brand.fonts.body}', {_FONT_FALLBACK}"
    if typo:
        tokens["typography"] = typo
    if brand.logo_asset_id:
        tokens["logo_asset_id"] = brand.logo_asset_id
        tokens["logo_alt"] = brand.logo_alt or f"{brand.name} logo"

    return _report(issues, theme_tokens=tokens, roles={**roles, "primary": primary,
                                                         "on_primary": on_primary},
                   contrast=contrast_report, adjustments=adjustments)


# --------------------------------------------------------------------------- #
# Görsel plan
# --------------------------------------------------------------------------- #
def lint_visual_plan(plan: VisualPlan, brand: BrandKit | None = None) -> dict:
    issues: list[dict] = []
    roles = resolve_roles(brand) if brand else None
    defined = set()
    if brand:
        defined = {k for k, v in brand.colors.model_dump().items() if v} | {"on_primary"}

    seen: set[str] = set()
    run_type, run_len = None, 0
    passive_run = 0
    accent_bg = 0
    has_check = False

    for i, s in enumerate(plan.screens):
        path = f"screens[{i}]({s.screen_id})"
        if s.screen_id in seen:
            issues.append(_issue("error", "duplicate_screen_id",
                                 f"screen_id '{s.screen_id}' is used twice", path))
        seen.add(s.screen_id)

        if len(_words(s.visual_concept)) < 6:
            issues.append(_issue("warn", "vague_visual_concept",
                                 "visual_concept should describe what the learner SEES "
                                 "(composition, subject, metaphor) in at least one full sentence",
                                 path))

        for j, img in enumerate(s.imagery):
            if not img.decorative and not (img.alt_text or "").strip():
                issues.append(_issue("error", "missing_alt_text",
                                     f"{img.kind} needs alt_text (or decorative=true)",
                                     f"{path}.imagery[{j}]"))

        n_words = len(_words(s.on_screen_text or ""))
        if n_words > MAX_ON_SCREEN_WORDS:
            issues.append(_issue("warn", "text_heavy_screen",
                                 f"{n_words} on-screen words (> {MAX_ON_SCREEN_WORDS}); move detail "
                                 "into narration or split the screen", path))

        if roles:
            for role in {s.background_role, s.text_role, s.accent_role} - {None}:
                if role not in defined:
                    issues.append(_issue("warn", "role_not_in_brand",
                                         f"color role '{role}' is not defined in the brand kit; "
                                         f"it falls back to {roles[role]}", path))
            ratio = _contrast(roles[s.text_role], roles[s.background_role])
            if ratio < AA_TEXT:
                issues.append(_issue("error", "low_contrast",
                                     f"text '{s.text_role}' on background '{s.background_role}' is "
                                     f"{ratio:.2f}:1 (< {AA_TEXT}:1)", path))
        if s.background_role == "accent":
            accent_bg += 1

        # monotonluk: aynı tip ≥3 art arda
        if s.screen_type == run_type:
            run_len += 1
        else:
            run_type, run_len = s.screen_type, 1
        if run_len == 3:
            issues.append(_issue("warn", "monotony",
                                 f"3 '{s.screen_type.value}' screens in a row — vary the format",
                                 path))

        if s.screen_type in PASSIVE_TYPES:
            passive_run += 1
            if passive_run == 5:
                issues.append(_issue("warn", "passive_stretch",
                                     "5 passive screens in a row — add an interaction or check",
                                     path))
        else:
            passive_run = 0
        if s.screen_type in SCORED_TYPES:
            has_check = True

    if not has_check:
        issues.append(_issue("warn", "no_knowledge_check",
                             "module has no scored/interactive check screen", "screens"))
    if accent_bg and accent_bg / len(plan.screens) > 0.10:
        issues.append(_issue("warn", "accent_overuse",
                             f"accent used as background on {accent_bg}/{len(plan.screens)} screens "
                             "— keep accent to ~10% (60-30-10 rule)", "screens"))

    return _report(issues, module_id=plan.module_id, screen_count=len(plan.screens))


# --------------------------------------------------------------------------- #
# Seslendirme metni
# --------------------------------------------------------------------------- #
def _wpm(script: NarrationScript) -> int:
    if script.wpm:
        return script.wpm
    return DEFAULT_WPM.get(script.language.split("-")[0].lower(), FALLBACK_WPM)


def _spoken(text: str) -> str:
    return re.sub(r"\s+", " ", _MARK_RE.sub(" ", text)).strip()


def _estimate_sec(text: str, wpm: int) -> float:
    pauses = sum(float(p) for p in _PAUSE_RE.findall(text))
    return round(len(_words(_spoken(text))) / wpm * 60.0 + pauses, 1)


def _sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?؟])\s+", _spoken(text)) if s.strip()]


def lint_narration_script(script: NarrationScript, plan: VisualPlan | None = None) -> dict:
    issues: list[dict] = []
    wpm = _wpm(script)
    plan_screens = {s.screen_id: s for s in plan.screens} if plan else {}
    lexicon = {k.upper() for k in script.lexicon}
    total = 0.0
    per_screen: list[dict] = []
    covered: set[str] = set()

    for i, seg in enumerate(script.segments):
        path = f"segments[{i}]({seg.screen_id}{'/' + seg.part if seg.part else ''})"
        spoken = _spoken(seg.narration)
        if not spoken:
            issues.append(_issue("error", "empty_narration", "narration is empty", path))
            continue
        covered.add(seg.screen_id)
        est = _estimate_sec(seg.narration, wpm)
        total += est
        per_screen.append({"screen_id": seg.screen_id, "part": seg.part, "words":
                           len(_words(spoken)), "est_sec": est})

        if plan and seg.screen_id not in plan_screens:
            issues.append(_issue("error", "unknown_screen",
                                 f"screen_id '{seg.screen_id}' is not in the visual plan", path))
        if est > MAX_SEGMENT_SEC:
            issues.append(_issue("warn", "segment_too_long",
                                 f"~{est}s of narration (> {MAX_SEGMENT_SEC:.0f}s) — split into "
                                 "parts/layers or another screen", path))
        if seg.target_sec and est > seg.target_sec * 1.15:
            issues.append(_issue("warn", "over_target_time",
                                 f"~{est}s vs target {seg.target_sec}s at {wpm} wpm", path))

        for sent in _sentences(seg.narration):
            n = len(_words(sent))
            if n > MAX_SENTENCE_WORDS:
                issues.append(_issue("warn", "long_sentence",
                                     f"{n}-word sentence — keep spoken sentences ≤ "
                                     f"{MAX_SENTENCE_WORDS} words: '{sent[:60]}…'", path))

        low = spoken.lower()
        for phrase in _SCREEN_TALK:
            if phrase in low:
                issues.append(_issue("warn", "screen_talk",
                                     f"avoid '{phrase}' — narrate the idea, not the interface",
                                     path))

        for acr in sorted(set(_ACRONYM_RE.findall(spoken))):
            if acr not in lexicon:
                issues.append(_issue("warn", "pronunciation_missing",
                                     f"'{acr}' has no lexicon entry — add how TTS/voice talent "
                                     "should say it", path))

        if seg.on_screen_text:
            ost = [w.lower() for w in _words(seg.on_screen_text)]
            if len(ost) >= REDUNDANCY_MIN_WORDS:
                narr = " ".join(w.lower() for w in _words(spoken))
                # ardışık 4'lü kelime dizileriyle birebir örtüşme oranı
                grams = [" ".join(ost[k:k + 4]) for k in range(len(ost) - 3)]
                hit = sum(1 for g in grams if g in narr)
                if grams and hit / len(grams) >= REDUNDANCY_RATIO:
                    issues.append(_issue("warn", "redundant_on_screen_text",
                                         "narration reads the on-screen text word for word — "
                                         "show keywords on screen, explain in voice", path))

        for cue in _CUE_RE.findall(seg.narration):
            ps = plan_screens.get(seg.screen_id)
            if ps is not None and ps.cue_targets and cue not in ps.cue_targets:
                issues.append(_issue("error", "unknown_cue_target",
                                     f"[[cue:{cue}]] is not in the plan's cue_targets "
                                     f"{ps.cue_targets}", path))

    if plan:
        for s in plan.screens:
            if s.screen_id not in covered and s.screen_type not in ASSESSMENT_TYPES:
                issues.append(_issue("warn", "missing_narration",
                                     f"plan screen '{s.screen_id}' ({s.screen_type.value}) has no "
                                     "narration segment", s.screen_id))

    return _report(issues, module_id=script.module_id, wpm=wpm,
                   total_est_sec=round(total, 1), total_est_min=round(total / 60, 1),
                   screens=per_screen)


def _cue_times(text: str, wpm: int) -> list[dict]:
    """[[cue:id]] işaretinin konuşma içindeki tahmini zamanı (öndeki kelime + duraklama)."""
    out, t = [], 0.0
    sec_per_word = 60.0 / wpm
    for tok in re.split(r"(\[\[[^\]]*\]\])", text):
        m_cue, m_pause = _CUE_RE.fullmatch(tok), _PAUSE_RE.fullmatch(tok)
        if m_cue:
            out.append({"cue": m_cue.group(1), "at_sec": round(t, 1)})
        elif m_pause:
            t += float(m_pause.group(1))
        else:
            t += len(_words(tok)) * sec_per_word
    return out


def _xml_escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def export_audio_script(script: NarrationScript) -> dict:
    """Seslendirme metnini üretim çıktılarına çevirir.

    Her segment için: tts_text (işaretsiz, sözlük okunuşları uygulanmış — synthesize_speech ya da
    harici TTS'e aynen verilir), ssml (<break>/<sub> ile), narration_text (ekranın CC/transkript
    alanı — okunuş DEĞİL orijinal yazım), önerilen dosya adı, tahmini süre ve cue zamanları.
    Ayrıca insan seslendirme sanatçısı için markdown tablo (voice_talent_md).
    """
    wpm = _wpm(script)
    lex = script.lexicon
    lex_re = (re.compile(r"\b(" + "|".join(re.escape(k) for k in
                                           sorted(lex, key=len, reverse=True)) + r")\b")
              if lex else None)
    items = []
    md = ["| # | Screen | Tone | Script | Est. sec |", "|---|---|---|---|---|"]
    for i, seg in enumerate(script.segments, 1):
        caption = _spoken(seg.narration)
        tts = lex_re.sub(lambda m: lex[m.group(1)], caption) if lex_re else caption
        ssml_body = _xml_escape(seg.narration)
        ssml_body = _CUE_RE.sub(lambda m: f'<mark name="{m.group(1)}"/>', ssml_body)
        ssml_body = _PAUSE_RE.sub(lambda m: f'<break time="{m.group(1)}s"/>', ssml_body)
        if lex_re:
            ssml_body = lex_re.sub(
                lambda m: f'<sub alias="{_xml_escape(lex[m.group(1)])}">{m.group(1)}</sub>',
                ssml_body)
        ssml_body = re.sub(r"\s+", " ", ssml_body).strip()
        ssml = f'<speak xml:lang="{script.language}">{ssml_body}</speak>'
        part = f"_{seg.part}" if seg.part else ""
        est = _estimate_sec(seg.narration, wpm)
        items.append({
            "screen_id": seg.screen_id,
            "part": seg.part,
            "filename": f"{script.module_id}_{seg.screen_id}{part}.mp3",
            "narration_text": caption,
            "tts_text": tts,
            "ssml": ssml,
            "est_sec": est,
            "cues": _cue_times(seg.narration, wpm),
        })
        script_cell = re.sub(r"\[\[pause:(\d+(?:\.\d+)?)\]\]", r"*(pause \1s)*",
                             _CUE_RE.sub("", seg.narration)).replace("|", "\\|")
        script_cell = re.sub(r"\s+", " ", script_cell).strip()
        label = seg.screen_id + (f"/{seg.part}" if seg.part else "")
        md.append(f"| {i} | {label} | {seg.tone or ''} | {script_cell} | {est} |")

    header = [f"# Voice-over script — {script.module_id}", "",
              f"Language: {script.language} · Pace: ~{wpm} wpm"
              + (f" · Voice: {script.voice.persona}" if script.voice.persona else ""), ""]
    if lex:
        header += ["**Pronunciation guide**", ""] + [f"- **{k}** → {v}" for k, v in lex.items()]
        header.append("")
    return {
        "module_id": script.module_id,
        "language": script.language,
        "wpm": wpm,
        "total_est_sec": round(sum(x["est_sec"] for x in items), 1),
        "segments": items,
        "voice_talent_md": "\n".join(header + md) + "\n",
    }
