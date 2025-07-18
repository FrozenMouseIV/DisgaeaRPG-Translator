import os
import json
import re
import time
from deep_translator import GoogleTranslator
import deepl

from Code.config import Config, Paths

class DictionaryTranslator:
    def __init__(self):
        folder_path = Paths.DICTIONARIES_DIR
        self.dictionary = {}
        if os.path.exists(folder_path):
            for filename in os.listdir(folder_path):
                if filename.endswith('.json'):  # Only load .json files
                    file_path = os.path.join(folder_path, filename)
                    with open(file_path, 'r', encoding='utf8') as f:
                        try:
                            dict_data = json.load(f)
                            self.dictionary.update(dict_data)  # Merge dictionary
                        except json.JSONDecodeError:
                            print(f"Warning: Skipping invalid JSON file {filename}")

    def translate(self, jp_text):
        return self.dictionary.get(jp_text)

    def has(self, jp_text):
        return jp_text in self.dictionary

class EffectTranslator:
    def __init__(self, path='./PatternDictionaries/EffectDictionary.json'):
        self.replacements = []
        if os.path.exists(path):
            with open(path, 'r', encoding='utf8') as f:
                raw_dict = json.load(f)
                # Sort keys by length desc so longer matches replace first
                # Compile regex patterns for better performance
                self.replacements = sorted(
                    [(re.compile(re.escape(k)), v) for k, v in raw_dict.items()],
                    key=lambda x: len(x[0].pattern),
                    reverse=True
                )

    def translate(self, text):
        result = text
        result = text
        for pattern, replacement in self.replacements:
            result = pattern.sub(replacement, result)
        return result

class Translator:
    def __init__(self):
        self.dict_translator = DictionaryTranslator()
        self.effect_translator = EffectTranslator()
        # Placeholder for external services
        self.files_for_deepl = ['stage', 'character', 'memory', 'episode', 'command']
        self.translator_google = GoogleTranslator(source='auto', target='en')
        self.translator_deepl = deepl.Translator(Config.DEEPL_API_KEY)
        # Validate DeepL key
        try:
            self.translator_deepl = deepl.Translator(Config.DEEPL_API_KEY)
            # Test request to validate the key
            usage = self.translator_deepl.get_usage()
            if usage.character.limit is None:
                print("⚠️  DeepL API key is valid, but usage limits are unknown.")
        except deepl.exceptions.AuthorizationException:
            print("       ├─ ❌ Invalid DeepL API key. Please check your configuration.")
            self.translator_deepl = None
        except Exception as e:
            print(f"⚠️  Failed to initialize DeepL translator: {e}")
            self.translator_deepl = None


    def translate(self, filename, field, value) -> str:
        if not value or not isinstance(value, str):
            return value

        # RULE: For "command" file, use regex-based EffectTranslator on 'description'
        if filename == "command" and field == "description_effect":
            return self.effect_translator.translate(value)

        # RULE: For other fields, try DictionaryTranslator first
        if self.dict_translator.has(value):
            return self.dict_translator.translate(value)

        # If no match found, fallback to external API
        if filename in self.files_for_deepl and Config.DEEPL_API_KEY != "YOUR API KEY HERE":
            return self._translate_deepl(value)
        else:
            return self._translate_google(value)

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