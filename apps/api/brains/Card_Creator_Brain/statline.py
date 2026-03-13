from typing import Any


def infer_statline(shell: dict[str, Any], mechanics: dict[str, Any]) -> tuple[str | None, str | None]:
    if not shell.get("needs_pt"):
        return None, None

    mv = int(shell.get("manaValue", 0) or 0)
    effects = mechanics.get("effects") or []
    keywords = mechanics.get("keywords") or []

    power = max(1, mv)
    toughness = max(1, mv)

    if "damage" in effects or "haste" in keywords:
        power += 1
    if "token" in effects or "lifegain" in effects or "vigilance" in keywords:
        toughness += 1
    if "draw" in effects or "flying" in keywords:
        power = max(1, power - 1)
    if mv >= 6:
        power += 1
        toughness += 2

    power = min(power, 9)
    toughness = min(toughness, 9)
    return str(power), str(toughness)
