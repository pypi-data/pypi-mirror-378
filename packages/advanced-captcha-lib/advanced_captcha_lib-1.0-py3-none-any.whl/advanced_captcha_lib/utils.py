import locale

def detect_language():
    lang = locale.getdefaultlocale()[0]
    if lang and lang.startswith("es"):
        return "es"
    return "en"
