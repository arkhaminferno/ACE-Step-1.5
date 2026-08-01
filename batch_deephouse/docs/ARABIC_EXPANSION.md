# Arabic Deep House — ACE-Step expansion notes for HAYA

Operational docs live in project skills:

| Skill | Role |
|---|---|
| `.claude/skills/acestep-arabic-instruments/` | Instrument director (sahb/naqr, maqam prompts, density) |
| `.claude/skills/acestep-arabic-deephouse-expand/` | Pipeline, LEGO, DoRA training, MPS patches |

## Immediate generation defaults

- Max **1 Sahb + 1 Naqr** per section; prefer solo dry oud.
- Caption must include instrument + maqam when Arabic color is required.
- Negatives (5 max): `no trumpet, no brass, no guzheng, no pipa, no harsh digital lead`
- Do **not** cover/repaint approved masters just to swap instruments.

## Phase 1 + 2 status (local)

| Item | Status |
|---|---|
| MPS watermark in `start_acestep_api.sh` / `env_mps.sh` | Done |
| ADG `.to(torch.float32)` in `apg_guidance.py` | Done |
| Cover strength clamp to 1.0 on MPS workaround | Done (`mps_safety.py`) |
| LEGO `thinking=False` helper | Done |
| Dataset folder + JSON schema examples | Done (`datasets/arabic_house_dataset/`) |
| `auto_label.py` CLI | Done (needs transcriber weights) |

## Phase 3 status

| Item | Status |
|---|---|
| Side-Step CLI wrapper `phase3_dora_train.sh` | Done (correct `train.py fixed` CLI) |
| `build_dataset_json.py` (sidecars → Side-Step JSON) | Done |
| Audio stems on disk | **BLOCKED — none found** (only examples JSON/lyrics) |
| Side-Step sibling install | **BLOCKED — not cloned** |
| `acestep-v15-base` / `sft` weights | Missing (turbo present; script falls back) |

### Run when ready

```bash
# 1) Put .mp3/.wav stems next to matching .json in arabic_house_dataset/
# 2) Clone Side-Step + uv sync (see training.md)
./batch_deephouse/scripts/phase3_dora_train.sh preprocess
./batch_deephouse/scripts/phase3_dora_train.sh estimate
./batch_deephouse/scripts/phase3_dora_train.sh train
```
