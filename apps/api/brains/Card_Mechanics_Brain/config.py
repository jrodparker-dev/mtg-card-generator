from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
API_DIR = THIS_DIR.parents[2]
DATA_DIR = API_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
MODELS_DIR = API_DIR / "models" / "Card-Mechanics-Brain"

SCRYFALL_DEFAULT_CARDS = RAW_DIR / "scryfall-default-cards.json"
TRAIN_ROWS_JSONL = PROCESSED_DIR / "mechanics_train_rows.jsonl"
LABEL_MAPS_JSON = MODELS_DIR / "label_maps.json"
MODEL_STATE = MODELS_DIR / "mechanics_brain.pt"
TRAINING_META_JSON = MODELS_DIR / "training_meta.json"

RANDOM_SEED = 42
MAX_KEYWORDS = 48
MAX_EFFECTS = 40
MAX_SUBTYPES = 128
MAX_NAME_TOKENS = 4
BATCH_SIZE = 128
EPOCHS = 14
LEARNING_RATE = 1e-3
HIDDEN_DIM = 256
DROPOUT = 0.18
MIN_LABEL_FREQ = 20
TOP_K_RETRIEVAL = 10
