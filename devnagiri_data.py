from indic_transliteration import sanscript
from indic_transliteration.sanscript import transliterate

# Devanagari text
devnagari_text = "विरामः"
sanskrit_words = [
    "शून्य",    # null  
    "सत्य",     # true  
    "असत्य",    # false  
    "पि",       # pi  
    "मुद्रयति",  # print  
    "मुद्रयति_पुनः",  # print_rt  
    "प्रवेशः",   # input  
    "अंक_प्रवेशः",  # input_int  
    "शुद्ध",     # clear/cls  
    "अंकः_वा",   # is_number  
    "सूत्रम्_वा",  # is_string  
    "सूचिः_वा",   # is_list  
    "कार्यः_वा",  # is_function  
    "संयोजयति",  # append  
    "अपनयति",    # pop  
    "प्रसारयति",  # extend  
    "परिमाणम्",   # len  
    "धावयति"     # run  
]

print(sanskrit_words)

for i in sanskrit_words:
    english_text = str(
        transliterate(i, sanscript.DEVANAGARI, sanscript.ITRANS)
    )

    print(english_text)  # Output: kr
# Transliterate Devanagari to English (IAST format)
english_text = str(
    transliterate(devnagari_text, sanscript.DEVANAGARI, sanscript.ITRANS)
)
print(english_text)  # Output: krishhNa
