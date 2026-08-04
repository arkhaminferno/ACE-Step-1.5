# Arabic deep-house DoRA adapter (inference only)

Published from Windows Side-Step training via:

```bash
./batch_deephouse/scripts/publish_adapter_to_repo.sh best
```

## Layout

```
arabic_deep_house/
  ADAPTER_META.json
  best/
    adapter_config.json
    adapter_model.safetensors   # Git LFS
```

## Mac use

```bash
git lfs install
git pull
# API on :8001
./batch_deephouse/scripts/load_arabic_adapter_mac.sh best 0.45
```

Do **not** commit `checkpoints/`, `training_state.pt`, or full DiT weights here.
