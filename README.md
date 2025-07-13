# DisgaeaRPG-Translator

A project to translate Disgaea RPG JP to english

Requirements:

- Python v3.10+
- DeepL API Key (not necessary, but if not provided the google translate will be used instead)
- `pip install unitypy`
- `pip install deepl`
- `pip install deep_translator`

## Folder Structure for the project

- Source: dump of the game files
- Source_Translated: Translated files that will be patched into the game files
- Translated_Files: translated game file to be placed in the game folder
- Updated_Files: Used to keep track of what files have been modified after a game update
- Masters_Backup: Used to store a backup of the masters files

## Usage

- Set up your API key on config.py. Getting one is free. This isn't required, if you do not provide one, the Google Translate API will be used instead
