def build_mana_cost(primary_type: str, color_bucket: str, mana_value_bucket: str):
    if primary_type == "Land":
        return ""
    mv = 6 if mana_value_bucket == "6+" else int(mana_value_bucket or 0)
    if mv <= 0:
        return "{0}"

    colors = [] if color_bucket == "Colorless" else [c for c in color_bucket.split("/") if c]
    if not colors:
        return "{" + "}{".join([str(mv)]) + "}"

    pip_count = 1 if mv <= 2 else 2 if mv <= 5 else 3
    pip_count = min(pip_count, mv)
    generic = mv - pip_count
    parts = []
    if generic > 0:
        parts.append(str(generic))
    for i in range(pip_count):
        parts.append(colors[i % len(colors)])
    return "{" + "}{".join(parts) + "}"
