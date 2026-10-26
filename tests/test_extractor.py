"""Unit tests for document text extractor."""

import io
import docx
import pytest

from src.extractor import (
    EmptyFileError,
    ExtractionError,
    NoTextExtractedError,
    UnsupportedFormatError,
    extract_text,
    extract_text_from_docx,
    extract_text_from_pdf,
)


def test_extract_text_from_pdf_success(synthetic_pdf_bytes):
    """Test extracting readable text from valid PDF bytes."""
    text = extract_text_from_pdf(synthetic_pdf_bytes)
    assert "John Doe" in text
    assert "Python" in text
    assert "Docker" in text


def test_extract_text_from_pdf_empty_text_layer(synthetic_image_pdf_bytes):
    """Test that a PDF without text layer raises NoTextExtractedError."""
    with pytest.raises(NoTextExtractedError) as exc_info:
        extract_text_from_pdf(synthetic_image_pdf_bytes)
    assert "no extractable text layer" in str(exc_info.value).lower()


def test_extract_text_from_pdf_corrupt_bytes():
    """Test that corrupt PDF bytes raise ExtractionError."""
    corrupt = b"not a real pdf content header"
    with pytest.raises(ExtractionError):
        extract_text_from_pdf(corrupt)


def test_extract_text_from_docx_success(synthetic_docx_bytes):
    """Test extracting paragraphs and table cells from valid DOCX bytes."""
    text = extract_text_from_docx(synthetic_docx_bytes)
    assert "Jane Developer" in text
    assert "FastAPI" in text
    assert "Python | Expert" in text or ("Python" in text and "Expert" in text)


def test_extract_text_from_docx_empty():
    """Test that an empty DOCX raises NoTextExtractedError."""
    empty_doc = docx.Document()
    bio = io.BytesIO()
    empty_doc.save(bio)
    with pytest.raises(NoTextExtractedError):
        extract_text_from_docx(bio.getvalue())


def test_extract_text_from_docx_corrupt():
    """Test that corrupt DOCX bytes raise ExtractionError."""
    with pytest.raises(ExtractionError):
        extract_text_from_docx(b"corrupt docx data")


def test_extract_text_wrapper_pdf(synthetic_pdf_bytes):
    """Test wrapper extract_text with .pdf extension."""
    text = extract_text("resume.pdf", synthetic_pdf_bytes)
    assert "John Doe" in text


def test_extract_text_wrapper_docx(synthetic_docx_bytes):
    """Test wrapper extract_text with .docx extension."""
    text = extract_text("my_cv.docx", synthetic_docx_bytes)
    assert "Jane Developer" in text


def test_extract_text_empty_file():
    """Test that 0-byte file raises EmptyFileError."""
    with pytest.raises(EmptyFileError):
        extract_text("empty.pdf", b"")


def test_extract_text_unsupported_format():
    """Test that unsupported format raises UnsupportedFormatError."""
    with pytest.raises(UnsupportedFormatError):
        extract_text("resume.txt", b"plain text content")

    with pytest.raises(UnsupportedFormatError):
        extract_text("cv.png", b"image data")
