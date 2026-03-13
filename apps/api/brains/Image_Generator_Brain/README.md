# Image Generator Brain

This package gives you two things:

1. A **true trainable image brain** scaffold using a conditional VAE in PyTorch.
2. A **practical runtime image generator** that already works now via deterministic procedural card art.

## Main files

- `download_scryfall_art.py` — downloads Scryfall art crops
- `metadata_dataset.py` — builds training rows
- `dataset.py` — prompt/image dataset
- `model.py` — conditional VAE
- `train.py` — training loop
- `style_lora.py` — lightweight LoRA adapter primitive for later style tuning
- `image_generator.py` — runtime generator service used by Creator Brain

## Quick start

1. Download or build art refs.
2. Train the model.
3. Generate card art through Creator Brain.

If the model is not trained yet, the app still works with a procedural fallback image generator.
