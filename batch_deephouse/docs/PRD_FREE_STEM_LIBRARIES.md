# PRD: Free Instrument Stem Libraries for Multi-Project DoRA Training

**Status:** Draft for research  
**Owner:** HAYA / SoulCalm / CelebrateVibes production  
**Last updated:** 2026-08-05  
**Related:** `batch_deephouse/docs/ALL_PROJECTS_INSTRUMENT_TRAINING.md`, `arabic_house_dataset_v2/STEM_SOURCE_GUIDE.md`

---

## 1. Problem

ACE-Step base/turbo often renders Arabic leads (oud, qanun, ney, violin) as wrong timbres (e.g. guzheng-like). SoulCalm needs clear felt piano; Birthday needs festival EDM beds + classic piano/guitar.

We fine-tune with **Side-Step DoRA** on Windows (RTX 5070), then ship small adapters to Mac via Git LFS.

**Blocker:** Training needs **dry, legal instrument stems**. Manual Splice/Loopmasters shopping does not scale. We need **free (or free-for-our-use) libraries** we can script or bulk-import into named dataset slots.

---

## 2. Goals

| ID | Goal |
|----|------|
| G1 | Source **legal free/CC** dry stems for all three project adapters |
| G2 | Prefer sources that support **bulk download or API** (minimal manual work) |
| G3 | Map files into existing slot layouts (`*_v2` / soulcalm / birthday datasets) |
| G4 | Quality good enough that adapters improve timbre vs base model |
| G5 | Keep commercial/pirated packs **out of scope** |

### Non-goals

- Scraping Splice / Loopmasters / paid Kontakt libraries without a license  
- Training on ACE-Step / Suno generated “fake stems”  
- One mega-adapter mixing piano + Arabic + EDM (separate adapters only)  
- Shipping full base model weights in git  

---

## 3. Users & workflow

1. **Researcher (you):** find free libraries / datasets / APIs that match the instrument matrix.  
2. **Windows trainer:** run fetch/import scripts → preprocess → DoRA train → publish adapter.  
3. **Mac producer:** `git lfs pull` → load adapter → Recipe 4 / SoulCalm / Birthday generate.

---

## 4. Instrument requirements (research checklist)

### 4.1 Adapter A — Arabic / HAYA (`arabic_house_dataset_v2`)

| Priority | Instrument | Notes for researchers |
|----------|------------|------------------------|
| P0 | Oud (dry solo) | Close-mic, not full mix; Bayati/Rast/Hijaz if labeled |
| P0 | Qanun | Real qanun, not generic harp/guzheng |
| P0 | Arabic violin | Legato / slides; not erhu-labeled only |
| P0 | Ney / nay | Breathy flute; not sax |
| P1 | Santur | Hammered; short sparkle OK |
| P1 | Darbuka, riq | Dry loops; 100–120 BPM useful |
| P2 | Kick, sub, swung hats, pads | Deep-house bed elements ~108 BPM |
| P2 | Pluck, e-piano **stabs**, sparse guitar, buzuq, tabla | Experiment extras |

**Slots today:** 35 named JSON slots in `batch_deephouse/datasets/arabic_house_dataset_v2/`.

### 4.2 Adapter B — SoulCalm (`soulcalm_piano_dataset`)

| Priority | Instrument |
|----------|------------|
| P0 | Soft felt / upright / intimate piano solos |
| P0 | Warm retro / ambient synth pads |
| P2 | Rhodes/EP, soft strings, celesta |

### 4.3 Adapter C — Birthday (`birthday_edm_dataset`)

| Priority | Instrument |
|----------|------------|
| P0 | Four-on-floor kick, supersaw/bright synth, deep bass, claps |
| P1 | Upright/grand piano (classic/waltz), acoustic steel-string guitar |
| P2 | Party horns, pluck, light strings, light drums |

---

## 5. Stem quality bar (acceptance)

A clip is **acceptable** if:

- [ ] Single dominant instrument (or single bed element)  
- [ ] Relatively **dry** (short room OK; huge hall wash = reject)  
- [ ] Duration **5–120 s** (20–90 s ideal)  
- [ ] Not a full commercial song mix with vocals  
- [ ] License allows **ML training / derivative model weights** for our use (see §6)  
- [ ] Audible as the named instrument to a human listener  

**Reject:** guzheng mislabeled as oud/qanun, heavy FX walls, TikTok rips, AI-generated instrumentals.

---

## 6. Licensing requirements (critical for research)

When you evaluate a “free” library, record:

| Field | Required answer |
|-------|-----------------|
| License name | CC0 / CC-BY / CC-BY-SA / custom / unknown |
| Commercial use | Yes / No |
| ML / AI training allowed | Yes / No / Unclear |
| Attribution required | Yes / No — if yes, how |
| Share-alike implications | Does SA force us to open-source adapters? |
| Redistribution of raw stems in git | Allowed or “train-only, don’t republish samples”? |

**Prefer:** **CC0** or explicit “free for ML training.”  
**Caution:** CC-BY-SA may complicate shipping proprietary adapters — flag for legal review.  
**Avoid:** “Free for personal use only,” “no AI,” unknown scraped YouTube dumps.

---

## 7. Delivery formats we need from research

For each candidate source, fill a short card:

```text
Name:
URL:
License:
API / bulk download? (yes/no + how)
Instruments covered: (list)
Approx clip count / quality notes:
Import path: (scriptable / manual zip)
Blockers:
```

Ideal outcomes (any of these):

1. **API** (like Freesound) we can plug into `fetch_*_stems.py`  
2. **Bulk ZIP** of dry one-shots/loops we unzip into `raw/` then auto-map  
3. **Hugging Face dataset** with clear license + audio files  

---

## 8. Current automation (baseline)

| Capability | Status |
|------------|--------|
| Named empty slots + captions (Arabic v2) | Done — 35 slots |
| Freesound CC **preview** auto-fetch | Done — `batch_deephouse.datasets.fetch_freesound_stems` |
| SoulCalm / Birthday auto-fetch | Not built — wait for sources |
| Commercial pack scrapers | **Out of scope** |

Freesound previews are a **bootstrap**, not the final quality bar. Research should find **better free libraries** to replace/supplement them.

---

## 9. Volume targets

| Adapter | Minimum clips to start train | Strong set |
|---------|------------------------------|------------|
| Arabic | 20 | 40–60 |
| SoulCalm | 15 | 25–40 |
| Birthday | 20 | 40–60 |

---

## 10. Success metrics

| Metric | Target |
|--------|--------|
| Arabic slots with legal audio | ≥ 40 before serious DoRA |
| Human A/B: oud/qanun recognizable vs base | Clear win with adapter @ scale 0.35–0.55 |
| No license blockers for Mac publish | Adapter shippable under our repo policy |
| Manual minutes per new library | < 30 after first import script |

---

## 11. Research brief — what to find

Please hunt for **free alternatives** in these buckets:

1. **Arabic / MENA instrument sample packs** (CC0 / academic / cultural archives)  
2. **Felt / soft piano** free libraries (not bright concert grand only)  
3. **EDM one-shot kits** (kick, clap, bass, supersaw) with clear licenses  
4. **Ethnomusicology / university** downloadable corpora  
5. **Hugging Face** audio datasets tagged oud, qanun, ney, darbuka, etc.  
6. Anything with **bulk download or API** better than Freesound previews  

Out of scope unless licensed: torrents, “free” paid-pack leaks, YouTube-dl of copyrighted tracks.

---

## 12. After you find candidates

1. Paste source cards into an issue / reply (or `research/stem_sources.md`).  
2. We’ll add fetch/import scripts per source.  
3. Windows: import → count mp3s → `./scripts/train_project_adapter.sh …`  
4. Publish adapters only (not the 150 GB workspace) to Mac via git LFS.

---

## 13. Open questions for research

1. Which free Arabic packs are actually **qanun/oud** and not mis-tagged?  
2. Any CC0 MENA percussion loop packs at ~108 BPM?  
3. Felt-piano packs free for AI training?  
4. Can we use Philharmonia / similar orchestral samples for violin only?  
5. Attribution text we must keep if we use CC-BY?

---

## 14. Appendix — repo paths

| Path | Role |
|------|------|
| `batch_deephouse/datasets/arabic_house_dataset_v2/` | Arabic slots |
| `batch_deephouse/datasets/fetch_freesound_stems.py` | Current free auto-fetch |
| `batch_soulcalm/datasets/soulcalm_piano_dataset/` | Piano/pad slots |
| `batch_deephouse/datasets/templates/birthday_edm_dataset/` | Birthday templates |
| `scripts/train_project_adapter.sh` | Train entrypoint |
| `scripts/publish_project_adapter.sh` | Ship adapter to git |
