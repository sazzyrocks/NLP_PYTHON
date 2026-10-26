"""Text preprocessing module preserving technical terminology."""

import re

# Map tech tokens to protected alphanumeric placeholders before punctuation stripping
TECH_TOKENS_MAP = {
    r"\bc\+\+\b": "XTECHCPPX",
    r"\bc#\b": "XTECHCSHARPX",
    r"(?<![a-z0-9])\.net\b": "XTECHDOTNETX",
    r"\bnode\.js\b": "XTECHNODEJSX",
    r"\bnext\.js\b": "XTECHNEXTJSX",
    r"\bvue\.js\b": "XTECHVUEJSX",
    r"\breact\.js\b": "XTECHREACTJSX",
    r"\bexpress\.js\b": "XTECHEXPRESSJSX",
    r"\bci/cd\b": "XTECHCICDX",
    r"\bpl/sql\b": "XTECHPLSQLX",
    r"\btcp/ip\b": "XTECHTCPIPX",
    r"\brest\s+api\b": "XTECHRESTAPIX",
    r"\brestful\s+api\b": "XTECHRESTFULAPIX",
}

# Reverse mapping to restore preserved tokens
REVERSE_TECH_TOKENS_MAP = {
    "XTECHCPPX": "c++",
    "XTECHCSHARPX": "c#",
    "XTECHDOTNETX": ".net",
    "XTECHNODEJSX": "node.js",
    "XTECHNEXTJSX": "next.js",
    "XTECHVUEJSX": "vue.js",
    "XTECHREACTJSX": "react.js",
    "XTECHEXPRESSJSX": "express.js",
    "XTECHCICDX": "ci/cd",
    "XTECHPLSQLX": "pl/sql",
    "XTECHTCPIPX": "tcp/ip",
    "XTECHRESTAPIX": "rest api",
    "XTECHRESTFULAPIX": "restful api",
}

# Common bullet and symbol characters found in resumes
BULLET_CHARS = (
    r"[\u2022\u2023\u25E6\u2043\u2219\u25CB\u25CF\u25AA\u25AB\u25A0\u25B6\u25B8"
    r"\u2713\u2714\u27A2\u27A4\uF0B7\uF0A7\u25C6\u2013\u2014\*\-\>\|]"
)
BULLET_PATTERN = re.compile(BULLET_CHARS)

# Email and URL patterns
EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
URL_PATTERN = re.compile(r"(https?://\S+|www\.\S+)")

# Generic punctuation cleaner (preserves alphanumeric, protected placeholders, and whitespace)
PUNCT_PATTERN = re.compile(r"[^\w\s\+\#\./\-]")


def clean_text(text: str) -> str:
    """Clean and normalize resume or job description text.

    Steps:
    1. Lowercase text.
    2. Strip URLs and email addresses.
    3. Protect critical tech tokens (c++, c#, .net, node.js, ci/cd, rest api, etc.).
    4. Strip bullet points and unwanted symbols.
    5. Clean remaining punctuation while protecting tech tokens.
    6. Restore protected tech tokens.
    7. Normalize multi-whitespace and trim.

    Args:
        text: Raw input text.

    Returns:
        Cleaned, normalized text string.
    """
    if not text:
        return ""

    # 1. Lowercase
    cleaned = text.lower()

    # 2. Remove URLs and emails
    cleaned = URL_PATTERN.sub(" ", cleaned)
    cleaned = EMAIL_PATTERN.sub(" ", cleaned)

    # 3. Protect tech tokens
    for pattern, placeholder in TECH_TOKENS_MAP.items():
        cleaned = re.sub(pattern, f" {placeholder} ", cleaned)

    # 4. Strip bullets
    cleaned = BULLET_PATTERN.sub(" ", cleaned)

    # 5. Remove unwanted punctuation (quotes, braces, brackets, colons, semicolons, etc.)
    # We remove punctuation characters that are not part of placeholders
    cleaned = re.sub(r'["\'`~@$%^&*_=\[\]{}();:<>?\\|,!]', " ", cleaned)
    # Remove stand-alone slashes, pluses, dots, dashes that are not part of numbers/words
    cleaned = re.sub(r'(?<=\s)[/+\-](?=\s)', " ", cleaned)

    # 6. Restore protected tech tokens
    for placeholder, original in REVERSE_TECH_TOKENS_MAP.items():
        cleaned = cleaned.replace(placeholder, original)
        cleaned = cleaned.replace(placeholder.lower(), original)
        cleaned = cleaned.replace(placeholder.upper(), original)

    # 7. Normalize whitespace
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    return cleaned
