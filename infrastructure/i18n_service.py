"""
Internationalization service for translating UI text.
"""
import json
import os
from typing import Dict, Any, Optional
import streamlit as st


class I18nService:
    """Service to handle internationalization for the application."""
    
    def __init__(self, default_language="en"):
        """
        Initialize the I18n service.
        
        Args:
            default_language: The default language code to use
        """
        self.default_language = default_language
        self.translations: Dict[str, Dict[str, Any]] = {}
        self._load_translations()
    
    def _load_translations(self) -> None:
        """Load all translation files from the translations directory."""
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        translations_dir = os.path.join(base_dir, "translations")
        
        # Check if translations directory exists
        if not os.path.exists(translations_dir):
            print(f"Warning: Translations directory not found: {translations_dir}")
            return
        
        # Loop through language directories
        for lang_code in os.listdir(translations_dir):
            lang_dir = os.path.join(translations_dir, lang_code)
            if os.path.isdir(lang_dir):
                messages_file = os.path.join(lang_dir, "messages.json")
                if os.path.exists(messages_file):
                    try:
                        with open(messages_file, "r", encoding="utf-8") as f:
                            self.translations[lang_code] = json.load(f)
                    except Exception as e:
                        print(f"Error loading translation file {messages_file}: {str(e)}")
    
    def get_available_languages(self) -> list[str]:
        """
        Get a list of available language codes.
        
        Returns:
            List of available language codes
        """
        return list(self.translations.keys())
    
    def get(self, key: str, language: Optional[str] = None, **kwargs) -> str:
        """
        Get a translated string for the given key and language.
        
        Args:
            key: The translation key in dot notation (e.g., "app.title")
            language: The language code (defaults to the current language)
            **kwargs: Format arguments for the translation string
            
        Returns:
            The translated string
        """
        if language is None:
            language = self.get_current_language()
        
        # Try to get translation for the specified language
        translation = self._get_nested_value(self.translations.get(language, {}), key)
        
        # Fall back to default language if not found
        if translation is None and language != self.default_language:
            translation = self._get_nested_value(
                self.translations.get(self.default_language, {}), key
            )
        
        # If still not found, return the key itself
        if translation is None:
            return key
        
        # Format the translation string with the provided arguments
        try:
            if kwargs:
                return translation.format(**kwargs)
            return translation
        except (KeyError, ValueError):
            try:
                # Try positional formatting if keyword formatting fails
                return translation.format(*kwargs.values())
            except (KeyError, ValueError, IndexError):
                # Return as is if formatting fails
                return translation
    
    def _get_nested_value(self, data: Dict[str, Any], key: str) -> Optional[str]:
        """
        Get a nested value from a dictionary using dot notation.
        
        Args:
            data: The dictionary to search in
            key: The key in dot notation (e.g., "app.title")
            
        Returns:
            The value or None if not found
        """
        parts = key.split(".")
        current = data
        
        for part in parts:
            if not isinstance(current, dict) or part not in current:
                return None
            current = current[part]
        
        return current if isinstance(current, str) else None
    
    def get_current_language(self) -> str:
        """
        Get the current language code.
        
        Returns:
            The current language code
        """
        if "language" not in st.session_state:
            st.session_state.language = self.default_language
        return st.session_state.language
    
    def set_language(self, language: str) -> None:
        """
        Set the current language.
        
        Args:
            language: The language code to set
        """
        if language in self.translations:
            st.session_state.language = language