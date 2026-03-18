import re
from typing import List, Set

def extract_hashtags(text: str) -> Set[str]:
    """
    Extrae hashtags únicos de un texto.
    Ejemplo: "Hola #mundo #fastapi" -> {"mundo", "fastapi"}
    """
    if not text:
        return set()
    # Busca palabras que empiecen con # seguidas de caracteres alfanuméricos
    hashtags = re.findall(r"#(\w+)", text)
    return {tag.lower() for tag in hashtags}

def extract_mentions(text: str) -> Set[str]:
    """
    Extrae menciones a usuarios (@username) únicas de un texto.
    Ejemplo: "Hola @rodrigo @antigravity" -> {"rodrigo", "antigravity"}
    """
    if not text:
        return set()
    # Busca palabras que empiecen con @ seguidas de caracteres alfanuméricos
    mentions = re.findall(r"@(\w+)", text)
    return {username for username in mentions}
