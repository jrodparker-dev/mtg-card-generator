import {useState} from 'react';
import {generateCard} from './lib/api.js';
import CardInput from './components/CardInput.jsx';
import CardPreview from './components/CardPreview.jsx';

const fallbackCard = {
  name: 'Prototype Drake',
  mana_cost: '{2}{U}',
  type_line: 'Creature — Drake',
  rarity: 'Uncommon',
  oracle_text: ['Flying', 'When Prototype Drake enters, scry 1.'],
  power: '2',
  toughness: '3',
};

export default function App() {
  const [card, setCard] = useState(fallbackCard);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function onGenerate(name) {
    setLoading(true);
    setError('');
    try {
      const next = await generateCard(name);
      setCard(next.card ?? fallbackCard);
    } catch (err) {
      setError(err.message || 'Failed to generate card.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="page">
      <div className="panel">
        <h1>MTG Card Generator</h1>
        <p className="subtle">Starter shell wired for four trainable brains.</p>
        <CardInput onGenerate={onGenerate} loading={loading} />
        {error ? <div className="error">{error}</div> : null}
      </div>
      <CardPreview card={card} />
    </main>
  );
}
