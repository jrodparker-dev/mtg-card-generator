# Architecture

## Brains

### Card-Structure-Brain
Learns structural shells from Scryfall card metadata.

### Card-Mechanics-Brain
Will learn rules text, templating, and balance priors.

### Image-Generator-Brain
Will own prompt generation, training hooks, and future LoRA pipelines.

### Card-Creator-Brain
Will orchestrate all other brains and turn user input into a final card object.
