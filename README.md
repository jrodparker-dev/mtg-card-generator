# MTG Card Generator

This patch adds:
- final trainable **Card_Creator_Brain**
- full creator-to-structure-to-mechanics-to-image wiring
- a unified training guide for all brains

## Quick links
- Full training instructions: `docs/TRAINING_ALL_BRAINS.md`

## Runtime summary
`/generate-card` now does:

1. **Card_Creator_Brain** predicts a card concept from the name
2. **Card_Structure_Brain** refines the shell
3. **Card_Mechanics_Brain** generates oracle-style text
4. **Image_Generator_Brain** generates card art
5. The API returns a full card payload to the frontend
