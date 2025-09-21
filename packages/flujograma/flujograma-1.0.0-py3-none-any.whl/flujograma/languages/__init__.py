"""
Módulo de idiomas - Soporte para múltiples idiomas
"""

from .base import LanguageRules
from .es import SpanishRules
from .en import EnglishRules

__all__ = ["LanguageRules", "SpanishRules", "EnglishRules"]
