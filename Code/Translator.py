import os
import json
import re
import time
from deep_translator import GoogleTranslator
import deepl

from Code.config import Config, Paths

class DictionaryTranslator:
    def __init__(self, path='./Dictionaries/JP_to_EN_Dictionary.json'):
        self.dictionary = {}
        if os.path.exists(path):
            with open(path, 'r', encoding='utf8') as f:
                self.dictionary = json.load(f)

    def translate(self, jp_text):
        return self.dictionary.get(jp_text)

    def has(self, jp_text):
        return jp_text in self.dictionary


class EffectTranslator:
    def __init__(self, path='./Dictionaries/Effect_Replacement.json'):
        self.replacements = []
        if os.path.exists(path):
            with open(path, 'r', encoding='utf8') as f:
                raw_dict = json.load(f)
                # Sort by descending key length for priority replacement
                self.replacements = sorted(
                    raw_dict.items(),
                    key=lambda item: len(item[0]),
                    reverse=True
                )

    def translate(self, text):
        result = text
        for jp, en in self.replacements:
            pattern = re.escape(jp)
            result = re.sub(pattern, en, text)
        return result

class Translator:
    def __init__(self):
        self.dict_translator = DictionaryTranslator()
        self.effect_translator = EffectTranslator()
        # Placeholder for external services
        self.files_for_deepl = ['stage', 'character', 'memory', 'episode', 'command']
        self.translator_google = GoogleTranslator(source='auto', target='en')
        self.translator_deepl = deepl.Translator(Config.DEEPL_API_KEY)


    def translate(self, filename, field, value) -> str:
        if not value or not isinstance(value, str):
            return value

        # RULE: For "command" file, use regex-based EffectTranslator on 'description'
        if filename == "command" and field == "description_effect":
            return self.effect_translator.translate(value)

        # RULE: For other fields, use DictionaryTranslator
        if self.dict_translator.has(value):
            return self.dict_translator.translate(value)

        # Placeholder: If no match found, fallback to external API
        if filename in self.files_for_deepl:
            return self._translate_deepl(value)
        else:
            return self._translate_google(value)

        # If nothing matches, return original
        return value

    def _translate_deepl(self, text, max_retries=5, delay=5):
        for attempt in range(max_retries):
            try:
                result = self.translator_deepl.translate_text(text, target_lang="EN-US")
                return result.text
            except deepl.DeepLException as e:
                print(f"Attempt {attempt+1}/{max_retries} failed: {e}")
                if attempt < max_retries - 1:
                    print(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    raise  # re-raise the error if out of retries

    def _translate_google(self, text):
        return self.translator_google.translate(text)