def infer_subtypes(name: str, primary_type: str):
    low = name.lower()
    if primary_type == "Creature":
        if "angel" in low: return ["Angel"]
        if "dragon" in low: return ["Dragon"]
        if "goblin" in low: return ["Goblin", "Rogue"]
        if "witch" in low: return ["Warlock"]
        if "archivist" in low: return ["Wizard"]
        if "hydra" in low: return ["Hydra"]
        if "knight" in low: return ["Knight"]
        return ["Wizard"] if "oracle" in low or "seer" in low else ["Beast"]
    if primary_type == "Artifact":
        return ["Equipment"] if "blade" in low or "spear" in low else []
    if primary_type == "Enchantment":
        return ["Aura"] if "curse" in low or "blessing" in low else []
    if primary_type == "Land":
        return ["Forest"] if "forest" in low else ["Lair"] if "lair" in low else []
    return []

def build_type_line(name: str, primary_type: str, is_legendary: bool):
    supertypes = ["Legendary"] if is_legendary and primary_type in {"Creature", "Artifact", "Enchantment", "Land", "Planeswalker"} else []
    subtypes = infer_subtypes(name, primary_type)
    left = " ".join(supertypes + [primary_type]).strip()
    if subtypes:
        return f"{left} — {' '.join(subtypes)}"
    return left
