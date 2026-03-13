# Card Mechanics Brain

This package is the trainable mechanics layer for the MTG card generator.

## What it learns
- keyword distributions (flying, haste, vigilance, etc.)
- trigger patterns (ETB, dies, upkeep, activated, attack, combat-damage, static)
- effect families (draw, damage, token, removal, ramp, recursion, counters, discard, etc.)
- complexity bucket (simple / medium / complex)
- text line count bucket
- synergy between the structure shell and likely mechanics

## What it does not try to do yet
It is **not** a full end-to-end large language model that emits raw oracle text directly.
Instead, it uses a true supervised learning model to predict card-mechanics labels, then renders legal-ish oracle text from constrained templates.
That makes it trainable, fast, debuggable, and much easier to combine with the other brains.

## Expected input shell
The structure brain or card creator should pass a shell like:

```json
{
  "name": "Goblin Taxman",
  "types": ["Creature"],
  "subtypes": ["Goblin", "Rogue"],
  "colors": ["R"],
  "rarity": "Uncommon",
  "manaValue": 2,
  "isLegendary": false,
  "needsPowerToughness": true,
  "needsLoyalty": false,
  "power": "2",
  "toughness": "1"
}
```

## Training flow
1. `download_scryfall.py` downloads Scryfall bulk data.
2. `build_dataset.py` parses the oracle text into trainable labels.
3. `train.py` trains a multi-head neural model.
4. `infer.py` or `infer_service.py` predicts mechanics for a new shell.
5. `text_renderer.py` turns predictions into oracle text.

## Output shape

```json
{
  "keywords": ["Haste"],
  "trigger": "combat_damage_to_player",
  "effects": ["treasure"],
  "complexity": "simple",
  "lineCount": 2,
  "oracleText": [
    "Haste",
    "Whenever Goblin Taxman deals combat damage to a player, create a Treasure token."
  ]
}
```
