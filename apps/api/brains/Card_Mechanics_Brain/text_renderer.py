from typing import Any

COLOR_WORDS = {"W": "white", "U": "blue", "B": "black", "R": "red", "G": "green", "C": "colorless"}


def _name(shell: dict[str, Any]) -> str:
    return shell.get("name") or "This creature"


def render_keywords(pred: dict[str, Any]) -> list[str]:
    kws = pred.get("keywords") or []
    if not kws:
        return []
    top = kws[:2]
    return [", ".join(top)]


def render_effect_line(shell: dict[str, Any], pred: dict[str, Any]) -> str:
    trigger = pred.get("trigger", "none")
    effects = pred.get("effects") or ["vanilla"]
    card_name = _name(shell)
    primary = effects[0]
    color_word = COLOR_WORDS.get((shell.get("colors") or ["C"])[0], "colorless")

    if primary == "treasure":
        action = "create a Treasure token"
    elif primary == "token":
        sub = (shell.get("subtypes") or ["Spirit"])[0]
        action = f"create a 1/1 {color_word} {sub} creature token"
    elif primary == "draw":
        action = "draw a card"
    elif primary == "damage":
        action = f"it deals {max(1, int(shell.get('manaValue', shell.get('mana_value', 1)) // 2 or 1))} damage to any target"
    elif primary == "removal":
        action = "destroy target creature with mana value 3 or less"
    elif primary == "lifegain":
        action = "you gain 3 life"
    elif primary == "discard":
        action = "target opponent discards a card"
    elif primary == "mill":
        action = "target player mills three cards"
    elif primary == "ramp":
        action = "search your library for a basic land card, reveal it, put it into your hand, then shuffle"
    elif primary == "counters":
        action = "put a +1/+1 counter on target creature"
    elif primary == "counterspell":
        action = "counter target spell unless its controller pays {2}"
    elif primary == "loot":
        action = "draw a card, then discard a card"
    elif primary == "impulse":
        action = "exile the top card of your library. You may play it until the end of your next turn"
    elif primary == "reanimate":
        action = "return target creature card from your graveyard to the battlefield tapped"
    elif primary == "recur_hand":
        action = "return target card from your graveyard to your hand"
    elif primary == "bounce":
        action = "return target nonland permanent to its owner's hand"
    elif primary == "tap":
        action = "tap target creature"
    elif primary == "untap":
        action = "untap up to one target permanent"
    elif primary == "blink":
        action = "exile up to one target creature you control, then return that card to the battlefield under its owner's control"
    elif primary == "sacrifice":
        action = "target player sacrifices a creature"
    elif primary == "scry":
        action = "scry 2"
    elif primary == "surveil":
        action = "surveil 2"
    else:
        action = ""

    if not action:
        return ""

    if trigger == "etb":
        return f"When {card_name} enters the battlefield, {action}."
    if trigger == "dies":
        return f"When {card_name} dies, {action}."
    if trigger == "attack":
        return f"Whenever {card_name} attacks, {action}."
    if trigger == "combat_damage_to_player":
        return f"Whenever {card_name} deals combat damage to a player, {action}."
    if trigger == "upkeep":
        return f"At the beginning of your upkeep, {action}."
    if trigger == "end_step":
        return f"At the beginning of the end step, {action}."
    if trigger == "cast":
        return f"Whenever you cast a spell, {action}."
    if trigger == "activated":
        cost = "{1}, {T}" if shell.get("types") and "Creature" not in shell["types"] else "{2}"
        return f"{cost}: {action[0].upper()}{action[1:]}."
    if trigger == "static":
        return f"Creatures you control get +1/+0."
    return action[0].upper() + action[1:] + "."


def render_oracle_text(shell: dict[str, Any], pred: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    lines.extend(render_keywords(pred))
    effect_line = render_effect_line(shell, pred)
    if effect_line:
        lines.append(effect_line)
    if not lines and shell.get("types") and "Creature" in shell["types"]:
        lines.append("")
    return [line for line in lines if line.strip()]
