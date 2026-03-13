import {useState} from 'react';

export default function CardInput({onGenerate, loading}) {
  const [value, setValue] = useState('');

  function submit(e) {
    e.preventDefault();
    onGenerate(value.trim());
  }

  return (
    <form className="card-input" onSubmit={submit}>
      <input
        maxLength={20}
        placeholder="Enter a card name"
        value={value}
        onChange={(e) => setValue(e.target.value)}
      />
      <button type="submit" disabled={loading}>{loading ? 'Generating...' : 'Generate'}</button>
      <button type="button" disabled={loading} onClick={() => onGenerate('')}>Random</button>
    </form>
  );
}
