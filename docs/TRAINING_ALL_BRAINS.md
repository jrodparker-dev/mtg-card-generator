# Training Guide: All Brains

This project has four brains.

## 0. Shared prerequisite
Download Scryfall default cards first if you have not already.

### Option A: use an existing downloader in your project
If your starter already has a Scryfall bulk-data downloader, run that first.

### Option B: use the Image Brain downloader
```bash
cd apps/api
python -m brains.Image_Generator_Brain.download_scryfall_art
```

That will also fetch art crops. If you only want card JSON for Structure / Mechanics / Creator, you can keep your existing bulk downloader and skip a large art pull.

---

## 1. Card-Structure-Brain

### Purpose
Learns the card shell:
- primary type
- color bucket
- rarity
- mana value bucket
- needs P/T
- needs loyalty
- legendary flag

### Typical steps
Use the files that came with your Structure Brain package.

Common pattern:
```bash
cd apps/api
python -m brains.Card_Structure_Brain.build_dataset
python -m brains.Card_Structure_Brain.train
```

If your Structure package used different filenames, use those instead.

### Output
Expected checkpoint area:
```text
apps/api/models/Card-Structure-Brain/
```

---

## 2. Card-Mechanics-Brain

### Purpose
Learns oracle-style text behavior:
- trigger style
- effects
- keywords
- complexity
- line count

### Train
```bash
cd apps/api
python -m brains.Card_Mechanics_Brain.build_dataset
python -m brains.Card_Mechanics_Brain.train
```

If your earlier package named the dataset builder differently, run the builder file included in that package first, then `train.py`.

### Output
Expected checkpoint area:
```text
apps/api/models/Card-Mechanics-Brain/
```

---

## 3. Image-Generator-Brain

### Purpose
Learns prompt-conditioned fantasy card art from downloaded Scryfall art crops.

### Step 1: download art crops
```bash
cd apps/api
python -m brains.Image_Generator_Brain.download_scryfall_art
```

### Step 2: build metadata rows
```bash
cd apps/api
python -m brains.Image_Generator_Brain.metadata_dataset
```

`metadata_dataset` now keeps only rows that have a local image file in `apps/api/data/raw/scryfall_art/`. If it reports skipped rows, rerun the download step to fill gaps before training.

### Step 3: train image model
```bash
cd apps/api
python -m brains.Image_Generator_Brain.train
```

### Output
Expected checkpoint area:
```text
apps/api/models/Image-Generator-Brain/
```

### Runtime note
If the image model is not trained yet, the app still works by using the procedural fallback art generator.

---

## 4. Card-Creator-Brain

### Purpose
Learns concept mapping from **name → card concept**:
- type
- color
- rarity
- mana bucket
- trigger
- likely effects
- likely keywords

### Step 1: build dataset
```bash
cd apps/api
python -m brains.Card_Creator_Brain.build_dataset
```

### Step 2: train
```bash
cd apps/api
python -m brains.Card_Creator_Brain.train
```

### Output
Expected checkpoint area:
```text
apps/api/models/Card-Creator-Brain/
```

---

## 5. Full runtime flow after training
When everything is wired correctly:

1. Frontend calls `/generate-card`
2. **Creator Brain** predicts concept from the name
3. **Structure Brain** refines shell fields
4. **Mechanics Brain** creates oracle text
5. **Image Brain** generates art
6. API returns the final card to the frontend

---

## 6. Minimal dev run
Backend:
```bash
cd apps/api
uvicorn main:app --reload
```

Frontend:
```bash
cd apps/web
npm install
npm run dev
```

---

## 7. Practical training order
Best order:
1. Structure Brain
2. Mechanics Brain
3. Creator Brain
4. Image Brain

That gives you a usable card generator earlier, while the art model can train later.
