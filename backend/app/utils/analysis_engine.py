from typing import Dict

def make_description(descriptor: Dict, method: str) -> str:
    """
    META      -> розмір + MIME
    STRUCT    -> додає розширення
    SEMANTIC  -> TODO: звернення до AI
    """
    if method == "META":
        return f"{descriptor['size_bytes']} bytes, {descriptor['mime_type']}"
    if method == "STRUCT":
        return (f"{descriptor['size_bytes']} bytes, {descriptor['mime_type']}, "
                f"ext={descriptor['file_type']}")
    if method == "SEMANTIC":
        return "Semantic description placeholder"
    return "Unknown method"