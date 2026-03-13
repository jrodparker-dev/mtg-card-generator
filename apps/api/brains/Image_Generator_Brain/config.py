from pathlib import Path

THIS_DIR = Path(__file__).resolve().parent
API_DIR = THIS_DIR.parents[2]
DATA_DIR = API_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
EXPORTS_DIR = DATA_DIR / "exports" / "generated_art"
ART_CACHE_DIR = DATA_DIR / "raw" / "scryfall_art"
MODELS_DIR = API_DIR / "models" / "Image-Generator-Brain"

SCRYFALL_DEFAULT_CARDS = RAW_DIR / "scryfall-default-cards.json"
ART_METADATA_JSONL = PROCESSED_DIR / "image_brain_rows.jsonl"
VOCAB_JSON = MODELS_DIR / "prompt_vocab.json"
MODEL_STATE = MODELS_DIR / "image_brain.pt"
TRAINING_META_JSON = MODELS_DIR / "training_meta.json"

IMAGE_SIZE = 128
LATENT_DIM = 96
PROMPT_DIM = 96
BATCH_SIZE = 32
EPOCHS = 8
LEARNING_RATE = 2e-4
BETA = 0.001

for path in [RAW_DIR, PROCESSED_DIR, EXPORTS_DIR, ART_CACHE_DIR, MODELS_DIR]:
    path.mkdir(parents=True, exist_ok=True)
