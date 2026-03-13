from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
API_DIR = THIS_DIR.parents[2]
DATA_DIR = API_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
MODELS_DIR = API_DIR / "models" / "Card-Creator-Brain"

SCRYFALL_DEFAULT_CARDS = RAW_DIR / "scryfall-default-cards.json"
DATASET_JSONL = PROCESSED_DIR / "creator_brain_rows.jsonl"
VOCAB_JSON = MODELS_DIR / "vocab.json"
LABEL_MAPS_JSON = MODELS_DIR / "label_maps.json"
MODEL_STATE = MODELS_DIR / "creator_brain.pt"
TRAINING_META_JSON = MODELS_DIR / "training_meta.json"

MAX_NAME_TOKENS = 8
EMBED_DIM = 64
HIDDEN_DIM = 192
BATCH_SIZE = 64
EPOCHS = 12
LEARNING_RATE = 2e-3

for path in [RAW_DIR, PROCESSED_DIR, MODELS_DIR]:
    path.mkdir(parents=True, exist_ok=True)
