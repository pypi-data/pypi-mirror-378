# swaach-text

A small, dependency-light toolkit for **Hinglish + social text cleaning**:
- Emoji → text tags (e.g., `😂 → [laughing]`)
- Accent/diacritics removal (`café → cafe`)
- Hashtag splitter (`#ThisIsGreat → This Is Great`)
- Hinglish shorthand expansion + filler removal
- Optional PII redaction

## Install
```bash
pip install swaach-text
```

## Quick use
```python
from swaach_text import normalize, Cleaner

print(normalize("Plz yaar tmrw call me 😂 at café #ThisIsGreat!!!"))
# -> "please tomorrow call me [laughing] at cafe This Is Great!"
```

### CLI
```bash
swaach-text "Plz tmrw call me 😂 at café #ThisIsGreat"
# please tomorrow call me [laughing] at cafe This Is Great
```

## Notes
- This is a starter library; extend `rules.py` with more shorthand/emoji.
- For issues/PRs, please include examples + tests.
