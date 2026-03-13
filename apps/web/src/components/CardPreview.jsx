export default function CardPreview({card}) {
  return (
    <section className="card-shell">
      <div className="card-name-row">
        <strong>{card.name}</strong>
        <span>{card.mana_cost || ''}</span>
      </div>

      <div className="art-box">
        {card.art_data_uri ? (
          <img src={card.art_data_uri} alt={card.name} className="art-image" />
        ) : (
          'Art will render here later'
        )}
      </div>

      <div className="type-line">{card.type_line}</div>

      <div className="text-box">
        {(card.oracle_text || []).map((line, idx) => (
          <p key={idx}>{line}</p>
        ))}
        {card.flavor_text ? <p className="flavor-line"><em>{card.flavor_text}</em></p> : null}
      </div>

      {card.power && card.toughness ? (
        <div className="pt-box">{card.power}/{card.toughness}</div>
      ) : null}

      <div className="rarity-row">
        <div className="rarity">{card.rarity}</div>
        {card.generator_mode ? <div className="generator-mode">{card.generator_mode}</div> : null}
      </div>
    </section>
  );
}
