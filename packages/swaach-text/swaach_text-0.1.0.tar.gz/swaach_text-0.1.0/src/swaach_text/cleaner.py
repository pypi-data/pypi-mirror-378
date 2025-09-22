import re
from .rules import SHORTHAND, FILLERS, EMOJI_SIMPLE
from .emoji import emoji_to_text
from .textops import (
    remove_diacritics, expand_hashtags, collapse_repeats, tidy_spaces, redact_pii
)

class Preset:
    social = "social"
    reviews = "reviews"
    formal = "formal"

class Cleaner:
    def __init__(
        self,
        enable_shorthand: bool = True,
        enable_fillers: bool = True,
        enable_emoji_to_text: bool = True,
        enable_diacritics: bool = True,
        enable_hashtags: bool = True,
        enable_collapse_repeats: bool = True,
        enable_redact_pii: bool = False,
    ):
        self.enable_shorthand = enable_shorthand
        self.enable_fillers = enable_fillers
        self.enable_emoji_to_text = enable_emoji_to_text
        self.enable_diacritics = enable_diacritics
        self.enable_hashtags = enable_hashtags
        self.enable_collapse_repeats = enable_collapse_repeats
        self.enable_redact_pii = enable_redact_pii

    def _expand_shorthand(self, s: str) -> str:
        if not SHORTHAND:
            return s
        pat = r"\b(" + "|".join(map(re.escape, SHORTHAND.keys())) + r")\b"
        return re.sub(pat, lambda m: SHORTHAND[m.group(1).lower()], s, flags=re.I)

    def _remove_fillers(self, s: str) -> str:
        if not FILLERS:
            return s
        pat = r"\b(" + "|".join(map(re.escape, FILLERS)) + r")\b"
        return re.sub(pat, "", s, flags=re.I)

    def clean(self, s: str, preset: str | None = None) -> str:
        s = s.strip()

        if self.enable_collapse_repeats:
            s = collapse_repeats(s)
        if self.enable_emoji_to_text:
            s = emoji_to_text(s, EMOJI_SIMPLE)
        if self.enable_shorthand:
            s = self._expand_shorthand(s)
        if self.enable_fillers:
            s = self._remove_fillers(s)
        if self.enable_diacritics:
            s = remove_diacritics(s)
        if self.enable_hashtags:
            s = expand_hashtags(s)
        if self.enable_redact_pii:
            s = redact_pii(s)

        s = re.sub(r"\s+", " ", s)
        return tidy_spaces(s)

def normalize(text: str, preset: str = Preset.social) -> str:
    return Cleaner().clean(text, preset=preset)
