from typing import Any

FLAVOR_TEMPLATES = {
    "W": [
        "Even the ashes remembered the hymn.",
        "Its light found the faithful before the dawn did.",
    ],
    "U": [
        "It already knew what the tide would take.",
        "Every answer arrived a moment too early.",
    ],
    "B": [
        "What it touched kept breathing, but only technically.",
        "The price was small. The echoes were not.",
    ],
    "R": [
        "It laughed first. The battlefield answered.",
        "By the time the smoke cleared, the lesson had landed.",
    ],
    "G": [
        "Roots and teeth solved the argument together.",
        "No wall lasts long when the wild remembers your name.",
    ],
    "C": [
        "No priest had a name for the sound it made.",
        "It hummed like a secret older than metal.",
    ],
}


def generate_flavor_text(shell: dict[str, Any], mechanics: dict[str, Any]) -> str:
    colors = list(shell.get("colors") or ["C"])
    color = colors[0] if colors else "C"
    options = FLAVOR_TEMPLATES.get(color, FLAVOR_TEMPLATES["C"])
    index = (len(shell.get("name", "")) + len((mechanics.get("effects") or []))) % len(options)
    return options[index]
