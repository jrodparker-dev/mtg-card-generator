import re
from collections import Counter
from typing import Iterable

TOKEN_RE = re.compile(r"[a-zA-Z']+")


def tokenize_name(name: str) -> list[str]:
    return [token.lower() for token in TOKEN_RE.findall(name)]


def build_vocab(names: Iterable[str], min_freq: int = 1) -> dict[str, int]:
    counter: Counter[str] = Counter()
    for name in names:
        counter.update(tokenize_name(name))

    vocab = {'<PAD>': 0, '<UNK>': 1}
    for token, freq in sorted(counter.items()):
        if freq >= min_freq:
            vocab[token] = len(vocab)
    return vocab


def encode_name(name: str, vocab: dict[str, int], max_len: int = 6) -> list[int]:
    tokens = tokenize_name(name)[:max_len]
    encoded = [vocab.get(token, vocab['<UNK>']) for token in tokens]
    encoded.extend([vocab['<PAD>']] * (max_len - len(encoded)))
    return encoded
