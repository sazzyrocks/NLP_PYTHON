"""Unit tests for text preprocessing module."""

from src.preprocessing import clean_text


def test_clean_text_basic_normalization():
    """Verify lowercasing and multi-space collapse."""
    raw = "  Hello   WORLD!   This IS a   TEST.  "
    cleaned = clean_text(raw)
    assert cleaned == "hello world this is a test."


def test_clean_text_strips_urls_and_emails():
    """Verify URLs and emails are removed without leaving artifacts."""
    raw = "Contact dev@example.com or visit https://github.com/example/repo or www.test.org for info."
    cleaned = clean_text(raw)
    assert "dev@example.com" not in cleaned
    assert "https" not in cleaned
    assert "www.test.org" not in cleaned
    assert "contact" in cleaned
    assert "for info" in cleaned


def test_clean_text_preserves_tech_tokens():
    """Verify technical symbols like c++, c#, .net, node.js, ci/cd are preserved."""
    raw = (
        "Proficient in C++, C#, .NET, Node.js, Next.js, and Vue.js. "
        "Experienced with CI/CD and REST API design."
    )
    cleaned = clean_text(raw)
    assert "c++" in cleaned
    assert "c#" in cleaned
    assert ".net" in cleaned
    assert "node.js" in cleaned
    assert "next.js" in cleaned
    assert "vue.js" in cleaned
    assert "ci/cd" in cleaned
    assert "rest api" in cleaned


def test_clean_text_strips_bullets():
    """Verify bullet points of different unicode types are cleaned."""
    raw = "• Developed APIs\n◦ Managed databases\n▪ Deployed containers\n* Automated tests"
    cleaned = clean_text(raw)
    assert "•" not in cleaned
    assert "◦" not in cleaned
    assert "▪" not in cleaned
    assert "*" not in cleaned
    assert "developed apis" in cleaned
    assert "managed databases" in cleaned


def test_clean_text_empty_and_whitespace():
    """Verify empty or None text gracefully returns empty string."""
    assert clean_text("") == ""
    assert clean_text("   \n\t  ") == ""
    assert clean_text(None) == ""
