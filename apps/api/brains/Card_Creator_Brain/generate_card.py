from brains.Card_Creator_Brain.infer_service import load_creator_service
from brains.Card_Creator_Brain.mana_cost_builder import build_mana_cost
from brains.Card_Creator_Brain.type_line_builder import build_type_line
from brains.Card_Mechanics_Brain.infer_service import load_mechanics_service
from brains.Card_Structure_Brain.infer_service import load_structure_service
from brains.Image_Generator_Brain.image_generator import load_image_service

from .flavor_writer import generate_flavor_text
from .random_name import generate_random_name
from .statline import infer_statline

def _colors_from_bucket(bucket: str):
    if not bucket or bucket == "Colorless":
        return ["C"]
    return [c for c in bucket.split("/") if c]

def _concept_shell(name: str, concept: dict):
    type_line = build_type_line(name, concept["primary_type"], concept.get("is_legendary", False))
    mana_cost = build_mana_cost(concept["primary_type"], concept["color_bucket"], concept["mana_value_bucket"])
    mana_value = 6 if concept["mana_value_bucket"] == "6+" else int(concept["mana_value_bucket"])
    subtypes = type_line.split(" — ", 1)[1].split() if " — " in type_line else []
    return {
        "name": name,
        "colors": _colors_from_bucket(concept["color_bucket"]),
        "types": [concept["primary_type"]],
        "subtypes": subtypes,
        "rarity": concept["rarity"],
        "manaCost": mana_cost,
        "manaValue": mana_value,
        "needs_pt": concept.get("needs_pt", concept["primary_type"] == "Creature"),
        "needs_loyalty": concept.get("needs_loyalty", concept["primary_type"] == "Planeswalker"),
        "is_legendary": concept.get("is_legendary", False),
        "type_line": type_line,
        "primary_type": concept["primary_type"],
        "creator_concept": concept,
    }

def _merge_with_structure(name: str, concept: dict):
    structure = load_structure_service().infer(name)
    shell = _concept_shell(name, concept)

    if structure.get("primary_type") == shell["primary_type"]:
        if structure.get("rarity"):
            shell["rarity"] = structure["rarity"]
        if structure.get("mana_cost"):
            shell["manaCost"] = structure["mana_cost"]
        if structure.get("mana_value_bucket"):
            shell["manaValue"] = 6 if structure["mana_value_bucket"] == "6+" else int(structure["mana_value_bucket"])
        shell["needs_pt"] = bool(structure.get("needs_pt", shell["needs_pt"]))
        shell["needs_loyalty"] = bool(structure.get("needs_loyalty", shell["needs_loyalty"]))
        shell["is_legendary"] = bool(structure.get("is_legendary", shell["is_legendary"]))
        if structure.get("type_line"):
            shell["type_line"] = structure["type_line"]
            shell["subtypes"] = structure["type_line"].split(" — ", 1)[1].split() if " — " in structure["type_line"] else shell["subtypes"]
    return shell

def _normalize_oracle_text(lines):
    out = []
    for line in lines or []:
        line = " ".join(str(line).split())
        if line:
            out.append(line)
    return out[:3]

def generate_card_payload(name: str):
    card_name = (name or "").strip() or generate_random_name()
    concept = load_creator_service().predict_concept(card_name)
    shell = _merge_with_structure(card_name, concept)

    mechanics = load_mechanics_service().predict({**shell, "creator_concept": concept})
    if concept.get("effects"):
        for effect in concept["effects"]:
            if effect not in mechanics.get("effects", []):
                mechanics.setdefault("effects", []).append(effect)
    if concept.get("keywords"):
        for kw in concept["keywords"]:
            if kw not in mechanics.get("keywords", []):
                mechanics.setdefault("keywords", []).append(kw)
    shell["mechanics"] = mechanics

    power, toughness = infer_statline(shell, mechanics)
    flavor_text = generate_flavor_text(shell, mechanics)
    image_payload = load_image_service().generate({**shell, "oracleText": mechanics.get("oracleText", [])})

    payload = {
        "name": card_name,
        "mana_cost": shell["manaCost"],
        "mana_value": shell["manaValue"],
        "type_line": shell["type_line"],
        "rarity": shell["rarity"],
        "colors": shell["colors"],
        "oracle_text": _normalize_oracle_text(mechanics.get("oracleText", [])),
        "flavor_text": flavor_text,
        "art_prompt": image_payload["art_prompt"],
        "art_path": image_payload["art_path"],
        "art_data_uri": image_payload["art_data_uri"],
        "generator_mode": image_payload["generator_mode"],
    }
    if power is not None and toughness is not None:
        payload["power"] = power
        payload["toughness"] = toughness
    return payload
