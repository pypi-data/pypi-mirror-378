# pyass🍑/tests/test_translator.py

from pyass.engines.translator import Translator

def test_translator_basic():
    """Test basic translation"""
    translator = Translator()
    result = translator.translate("This is good", intensity=1.0)
    assert "good" not in result.lower(), "Should replace 'good'"
    assert any(word in result for word in ["bussin", "slay", "ate"]), "Should use slang for 'good'"

def test_translator_tone():
    """Test tone influence"""
    translator = Translator()
    dramatic = translator.translate("I am tired", tone="dramatic", intensity=1.0)
    print(f"[DEBUG] Dramatic translation: {dramatic}")
    expected_phrases = ["in shambles", "unalived", "deceased", "not alive"]
    assert any(phrase in dramatic.lower() for phrase in expected_phrases), (
        f"Should use dramatic slang. Got: {dramatic}")

def test_translator_persona():
    """Test persona influence"""
    translator = Translator()
    sigma = translator.translate("Hello", persona="sigma", intensity=1.0)
    # Sigma might use minimal/no slang — but let's check it doesn't break
    assert isinstance(sigma, str), "Should return string"
