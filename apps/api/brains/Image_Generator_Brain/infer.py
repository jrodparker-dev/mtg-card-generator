import json
import sys

from .image_generator import load_image_service


if __name__ == "__main__":
    shell = {
        "name": sys.argv[1] if len(sys.argv) > 1 else "Ashen Cathedral Angel",
        "colors": ["W"],
        "types": ["Creature"],
        "subtypes": ["Angel"],
        "rarity": "Mythic",
        "mechanics": {"effects": ["token", "lifegain"]},
    }
    print(json.dumps(load_image_service().generate(shell), indent=2))
