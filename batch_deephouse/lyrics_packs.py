"""Arabic lyric packs — hook-first, stupidly simple, high repetition."""

from __future__ import annotations


def _hook_block(phrase: str, times: int = 4) -> str:
    """Repeat a short hook phrase for earworm density."""
    line = phrase.strip()
    return "\n".join([line] * times)


LYRICS_BY_SLUG: dict[str, str] = {
    "yalil": f"""[Hook]
{_hook_block("يا ليل يا ليلي")}

[Verse]
في عيني كلام يبقى
أحلى من كل الأغاني
والليل يحفظ سرّي
والعود يرد بهدوء

[Hook]
{_hook_block("يا ليل يا ليلي")}

[Chorus]
يا ليل يا ليلي
خذني بعيداً بهدوء
يا ليل يا ليلي
لحن يبقى في قلبي

[Break]
(clear dry oud motif — sticky, present, no muffle)

[Hook]
{_hook_block("يا ليل يا ليلي")}

[Outro]
يا ليل يا ليلي
يا ليل يا ليلي
(soft natural fade)
""",
    "noor": f"""[Hook]
{_hook_block("نور نور")}

[Verse]
في عيني نور هادي
يغني بهدوء لقلبي
لحن خفيف يلفّني
والنبض يمشي معي

[Hook]
{_hook_block("نور نور")}

[Chorus]
نور نور يا حبيبي
نور نور لا تبعد
نور نور
نور نور

[Break]
(clear soft kick + sticky melodic motif — glowing, present)

[Hook]
{_hook_block("نور نور")}

[Outro]
نور نور
(soft natural fade)
""",
    # Full vocal song — verses + chorus, not hook-only.
    "gharib": """[Intro — soft groove, no vocal yet]

[Verse 1 — intimate female vocal, storytelling]
شفتك من بعيد
ما أعرف اسمك
بس قلبي ينادي
يا غريبي

[Pre-Chorus — building]
قرب شوي
لا تبعد عني
أحسّك قريب
وأنت غريب

[Chorus — bigger, clear]
يا غريبي
أنت غريبي
خدني معاك
يا غريبي

[Verse 2 — softer, more words]
كل ليلة أفكّر
في عيونك بهدوء
ما تقول لي كلام
بس أحسّك جوايا

[Chorus]
يا غريبي
أنت غريبي
خدني معاك
يا غريبي

[Bridge — breathy]
لو تبقى لحظة
ما أسأل مين أنت
بس غنّي لي
يا غريبي

[Chorus — final]
يا غريبي
أنت غريبي
خدني معاك
يا غريبي

[Outro — soft]
يا غريبي
(fade)
""",
    # Cover of local reference beat (Mi Chico groove) — all-new Arabic vocal.
    "hayati": """[Intro — keep the source beat, no vocal yet]

[Verse 1 — warm female vocal, playful]
شفتك والدنيا ضحكت
قلبي رقص على صوتك
خطوة منك تكفيني
تنسيني كل الدنيا

[Pre-Chorus — building]
تعال قرب شوي
الليل لسه طويل
معاك أحلى الليالي
يا حياتي

[Chorus — big, catchy]
يا حياتي يا حياتي
أنت نور عيوني
يا حياتي يا حياتي
خدني وين ما تروح

[Verse 2 — softer]
كلمة منك تحييني
ضحكتك أغلى غنوة
وين ما تمشي أمشي وياك
قلبي صار بيدك

[Chorus]
يا حياتي يا حياتي
أنت نور عيوني
يا حياتي يا حياتي
خدني وين ما تروح

[Bridge — breathy, half-time feel]
لو تغيب لحظة
الدنيا توقف عندي
ارجع لي بسرعة
يا حياتي

[Chorus — final, confident]
يا حياتي يا حياتي
أنت نور عيوني
يا حياتي يا حياتي
خدني وين ما تروح

[Outro]
يا حياتي
(soft fade)
""",
}
