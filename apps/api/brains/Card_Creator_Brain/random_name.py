import random

ADJECTIVES = [
    "Ashen", "Solar", "Void", "Cathedral", "Gilded", "Bog", "Storm", "Blood", "Whispering",
    "Runic", "Ember", "Ivory", "Wicked", "Dream", "Iron", "Dawn", "Twilight", "Verdant",
]
NOUNS = [
    "Angel", "Engine", "Taxman", "Witch", "Titan", "Archivist", "Dragon", "Priest", "Oracle",
    "Knight", "Seer", "Chimera", "Lantern", "Relic", "Hydra", "Goblin", "Beast", "Spire",
]


def generate_random_name() -> str:
    left = random.choice(ADJECTIVES)
    right = random.choice(NOUNS)
    return f"{left} {right}"
