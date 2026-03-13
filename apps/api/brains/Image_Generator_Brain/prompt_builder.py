from typing import Any

COLOR_WORDS = {
    "W": "radiant ivory and gold",
    "U": "deep blue and silver",
    "B": "shadowed violet and black",
    "R": "ember red and orange",
    "G": "lush green and earthy bronze",
    "C": "metallic steel and arcane teal",
}

TYPE_SCENES = {
    "Creature": "a character-focused fantasy illustration",
    "Artifact": "an ornate magical object framed dramatically",
    "Enchantment": "a mystical supernatural scene",
    "Instant": "a burst of action caught mid-spell",
    "Sorcery": "a cinematic spellcasting moment",
    "Planeswalker": "a legendary mage in a dramatic pose",
    "Land": "an epic fantasy landscape",
    "Battle": "a wide battlefield tableau",
}


def build_art_prompt(card: dict[str, Any]) -> str:
    colors = list(card.get("colors") or ["C"])
    primary_color = COLOR_WORDS.get(colors[0], COLOR_WORDS["C"])
    primary_type = (card.get("types") or ["Creature"])[0]
    subtypes = " ".join(card.get("subtypes") or [])
    rarity = str(card.get("rarity") or "Common").lower()
    effects = ", ".join((card.get("mechanics") or {}).get("effects", [])[:2]) or "fantasy magic"
    scene = TYPE_SCENES.get(primary_type, TYPE_SCENES["Creature"])
    name = card.get("name") or "Unknown Card"

    return (
        f"Polished fantasy trading card art for '{name}', {scene}, "
        f"{subtypes.lower() or 'mysterious figure'}, {primary_color}, "
        f"{rarity} rarity atmosphere, hint of {effects}, "
        f"painterly lighting, readable silhouette, premium card-art finish, no text, no border."
    )
