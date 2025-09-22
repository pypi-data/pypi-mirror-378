import re
import unicodedata

# Regex helpers
_RE_CAMEL = re.compile(r"(?<=[a-z])(?=[A-Z])")
_RE_REPEATS = re.compile(r"(.)\1{2,}")      # goooood -> good
_RE_PUNCT = re.compile(r"([!?.])\1{1,}")    # !!!?? -> ! ?

def remove_diacritics(s: str) -> str:
    # café -> cafe (NFKD normalize & drop combining marks)
    nfkd = unicodedata.normalize("NFKD", s)
    return "".join(ch for ch in nfkd if not unicodedata.combining(ch))

def _split_camel(s: str) -> str:
    s = _RE_CAMEL.sub(" ", s)
    s = re.sub(r"_", " ", s)
    s = re.sub(r"(\d)([A-Za-z])", r"\1 \2", s)
    s = re.sub(r"([A-Za-z])(\d)", r"\1 \2", s)
    return " ".join(s.split())

def expand_hashtags(s: str) -> str:
    # Replace hashtags with readable words: #ThisIsGreat -> This Is Great
    return re.sub(r"#\w[\w_]*", lambda m: _split_camel(m.group(0).lstrip("#")), s)

def collapse_repeats(s: str) -> str:
    s = _RE_REPEATS.sub(r"\1\1", s)
    s = _RE_PUNCT.sub(r"\1", s)
    return s

def tidy_spaces(s: str) -> str:
    return re.sub(r"\s{2,}", " ", s).strip()

def redact_pii(s: str) -> str:
    # Very light PII masking for demo: phone & email
    s = re.sub(r"\b(?:\+?\d[\d -]{7,}\d)\b", "[PHONE]", s)
    s = re.sub(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", "[EMAIL]", s, flags=re.I)
    return s
