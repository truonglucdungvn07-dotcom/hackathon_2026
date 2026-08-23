# utils/translator.py
import time
from deep_translator import GoogleTranslator, MyMemoryTranslator

def translate_safely(text, google_translator, fallback_translator):
    if not text or not text.strip():
        return ""

    for attempt in range(2):
        try:
            translated = google_translator.translate(text)
            if translated:
                return translated
        except Exception:
            if attempt == 0:
                time.sleep(1.5)

    try:
        if len(text) <= 500:
            translated = fallback_translator.translate(text)
            if translated:
                return translated
    except Exception:
        pass

    return text
