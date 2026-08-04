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
| Audio stems on disk | **2 stems** (oud + ney) — need **20–50+** for a real adapter |
| Side-Step sibling install | Clone to `../Side-Step` (see `TRAIN_MAC_PC.md`) |
| `acestep-v15-base` | Present under `checkpoints/` |
| Mac vs PC | **Train on NVIDIA Windows/Linux; generate on Mac** — see `TRAIN_MAC_PC.md` |

### Mac (M4 Pro 24 GB) vs Windows PC

- **Do not rely on this Mac for full DoRA training** — MPS often OOMs (even 36 GB Macs).
- **Train on a Windows NVIDIA PC (≥16 GB VRAM)** → copy `output/arabic_deep_house_dora/best` to Mac → load LoRA → Recipe 4 generate.
- Full cross-machine steps: **`batch_deephouse/docs/TRAIN_MAC_PC.md`**.

### Run when ready (on the CUDA training machine)

```bash
# 1) Put .mp3/.wav stems next to matching .json in arabic_house_dataset/
# 2) Clone Side-Step: git clone https://github.com/koda-dernet/Side-Step.git ../Side-Step
./batch_deephouse/scripts/phase3_dora_train.sh preprocess
./batch_deephouse/scripts/phase3_dora_train.sh analyze
./batch_deephouse/scripts/phase3_dora_train.sh train
```
