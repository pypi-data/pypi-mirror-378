def locale_string(lang, label, default_lang='en'):
    if lang != None:
        locale=lang.lower()
    else:
        locale = default_lang.lower()
    if isinstance(label, dict):
        return label.get(locale, label)
    return label
