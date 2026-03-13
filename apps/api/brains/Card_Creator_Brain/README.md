# Card Creator Brain

This is the final orchestration + concept-learning brain.

## What it learns
Given only the **card name**, it learns to predict:
- primary type
- rarity
- color bucket
- mana value bucket
- trigger style
- whether the card needs P/T
- whether it needs loyalty
- whether it is legendary
- likely effects
- likely keywords

## Training

### 1. Build the dataset
```bash
cd apps/api
python -m brains.Card_Creator_Brain.build_dataset
```

### 2. Train the model
```bash
cd apps/api
python -m brains.Card_Creator_Brain.train
```

### 3. Runtime
The API automatically uses the trained model if these files exist:
- `apps/api/models/Card-Creator-Brain/creator_brain.pt`
- `vocab.json`
- `label_maps.json`
- `training_meta.json`

Otherwise it falls back to heuristics.

## Role in the full pipeline
1. **Creator Brain** predicts the concept from the name.
2. **Structure Brain** refines the shell.
3. **Mechanics Brain** writes the text box.
4. **Image Brain** generates the art.
