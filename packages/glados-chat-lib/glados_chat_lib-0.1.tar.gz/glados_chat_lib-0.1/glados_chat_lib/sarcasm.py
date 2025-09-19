import re

def detect_sarcasm(text: str):
    text_lower = text.lower()
    markers = [
        r"\\byea?h,? right\\b",
        r"\\bsure\\b",
        r"\\bas if\\b",
        r"\\boh great\\b",
        r"\\bi love (that|how)\\b",
        r"\\bthanks for nothing\\b",
        r"\\bwow\\b.*not\\b"
    ]
    for pattern in markers:
        if re.search(pattern, text_lower):
            return True
    return False
