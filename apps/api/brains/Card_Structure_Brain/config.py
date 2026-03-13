from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = BASE_DIR / 'data' / 'raw'
PROCESSED_DIR = BASE_DIR / 'data' / 'processed'
CHECKPOINT_DIR = BASE_DIR / 'data' / 'checkpoints'

RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)

SCRYFALL_BULK_PATH = RAW_DIR / 'scryfall_default_cards.json'
STRUCTURE_DATASET_PATH = PROCESSED_DIR / 'card_structure_dataset.jsonl'
STRUCTURE_VOCAB_PATH = PROCESSED_DIR / 'card_structure_vocab.json'
STRUCTURE_MODEL_PATH = CHECKPOINT_DIR / 'card_structure_brain.pt'
