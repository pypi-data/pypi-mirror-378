import argparse
import sys
from .cleaner import Cleaner

def main():
    p = argparse.ArgumentParser(prog="swaach-text", description="Hinglish + social text normalizer")
    p.add_argument("text", nargs="+", help="Input text (quote if it has spaces)")
    p.add_argument("--keep-pii", action="store_true", help="Do not redact PII")
    p.add_argument("--no-emoji", action="store_true", help="Do not convert emojis to text")
    args = p.parse_args()

    cleaner = Cleaner(
        enable_redact_pii=not args.keep_pii,
        enable_emoji_to_text=not args.no_emoji
    )
    out = cleaner.clean(" ".join(args.text))
    sys.stdout.write(out + "\n")

if __name__ == "__main__":
    main()
