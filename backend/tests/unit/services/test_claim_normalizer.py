"""Tests for the rule-based claim normalizer (VeritasAd 2.0, M2 roadmap §7.1)."""
from app.services.claim_normalizer import normalize


def test_strips_scarcity_clause_keeps_measurable_core():
    out = normalize("Скидка до 70% только сегодня")
    assert "только сегодня" not in out.lower()
    assert "70%" in out


def test_strips_cta_noise():
    out = normalize("Скидка до 70%, переходи по ссылке в описании")
    assert "переходи" not in out.lower()
    assert "ссылк" not in out.lower()
    assert "70%" in out


def test_capitalizes_first_character():
    out = normalize("кэшбек 16% годовых")
    assert out[0] == "К"


def test_keeps_quantitative_upper_bound():
    # "до 70%" is preserved as an upper bound (not asserted as exactly 70%).
    out = normalize("до 70%")
    assert "до 70%" in out.lower()


def test_returns_trimmed_raw_when_cleanup_empties_it():
    # An all-CTA fragment is emptied by cleanup -> the trimmed raw text is returned.
    out = normalize("  жми подпишись  ")
    assert out == "жми подпишись"


def test_empty_input_returns_empty():
    assert normalize("") == ""


def test_strips_leading_filler():
    out = normalize("Кстати, скидка до 70%")
    assert "кстати" not in out.lower()
    assert "70%" in out
