# Arabic house dataset v2 (fresh)

JSON + lyrics slots are ready. **Add a matching `.mp3` for each id.**

Do **not** use ACE-Step-generated audio as stems.
See `STEM_SOURCE_GUIDE.md` in this folder.

Slots: **35** — fill as many as you can (aim 40+).
Train with:
```bash
AUDIO_DIR=batch_deephouse/datasets/arabic_house_dataset_v2 \
  ./scripts/train_project_adapter.sh arabic all
```
