from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

# Devanagari text
devnagari_text = "गणः"

# Transliterate Devanagari to English (IAST format)
english_text = str(transliterate(devnagari_text, sanscript.DEVANAGARI, sanscript.ITRANS))
print(english_text)  # Output: krishhNa