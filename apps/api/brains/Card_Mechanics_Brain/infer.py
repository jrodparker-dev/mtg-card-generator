import argparse
import json

from .infer_service import MechanicsBrainService


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True)
    parser.add_argument("--type", dest="card_type", default="Creature")
    parser.add_argument("--colors", default="R")
    parser.add_argument("--rarity", default="Uncommon")
    parser.add_argument("--mv", type=int, default=2)
    parser.add_argument("--subtypes", default="")
    args = parser.parse_args()

    shell = {
        "name": args.name,
        "types": [args.card_type],
        "subtypes": [s.strip() for s in args.subtypes.split(",") if s.strip()],
        "colors": [c.strip() for c in args.colors.split(",") if c.strip()],
        "rarity": args.rarity,
        "manaValue": args.mv,
        "needsPowerToughness": args.card_type == "Creature",
        "needsLoyalty": args.card_type == "Planeswalker",
        "isLegendary": False,
    }
    service = MechanicsBrainService()
    print(json.dumps(service.predict(shell), indent=2))


if __name__ == "__main__":
    main()
