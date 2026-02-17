def extract_text_content(content):
    """Extract text from message content that may be a string or list (with thinking blocks)."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(item for item in content if isinstance(item, str))
    return str(content)
