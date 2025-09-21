import emoji


def strip_emoji(text: str) -> str:
    if not text:
        return text
    text = emoji.replace_emoji(text)
    text = text.strip()
    return text
