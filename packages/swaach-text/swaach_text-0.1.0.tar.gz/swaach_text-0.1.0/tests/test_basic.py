from swaach_text import normalize, Cleaner

def test_shorthand_and_fillers():
    s = "Plz yaar tmrw call me"
    assert normalize(s) == "please tomorrow call me"

def test_emoji_and_diacritics():
    s = "café 😂"
    out = normalize(s)
    assert "cafe" in out and "[laughing]" in out

def test_hashtag_split():
    s = "Love #ThisIsGreat and #need_helpASAP"
    out = normalize(s)
    assert "This Is Great" in out
    assert "need help ASAP" in out

def test_cli_like():
    c = Cleaner(enable_redact_pii=True)
    s = "Plz dm at test@example.com or +91 98765 43210"
    out = c.clean(s)
    assert "[EMAIL]" in out and "[PHONE]" in out
