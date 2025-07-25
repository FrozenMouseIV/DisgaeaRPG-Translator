import json
import os
from pathlib import Path
import shutil
import tempfile

from Code.config import Paths

class Helper:
    def __init__(self):
        character_file_path = os.path.join(Paths.SOURCE_TRANSLATED_DIR, 'character.json')
        with open(character_file_path, 'r', encoding='utf8') as f:
            self.character_data = json.load(f)
        # Build lookup dict: id -> character data
        self.char_lookup = {char['id']: char for char in self.character_data}

        charactercommand_file_path = os.path.join(Paths.UPDATED_FILES_DIR, 'charactercommand.json')
        with open(charactercommand_file_path, 'r', encoding='utf8') as f:
            self.character_command_data = json.load(f)
        # Build lookup dict: m_command_id -> m_character_id
        self.character_command_lookup = {entry['m_command_id']: entry['m_character_id'] for entry in self.character_command_data}

    def find_character_by_leaderskill_id(self, leaderskill_id:int):
        for char in self.character_data:
            if leaderskill_id in (
                char.get("m_leader_skill_id"),
                char.get("additional_m_leader_skill_id"),
                char.get("m_leader_skill_id_sub_1"),
                char.get("additional_m_leader_skill_id_sub_1"),
                char.get("m_leader_skill_id_sub_2"),
                char.get("additional_m_leader_skill_id_sub_2"),
                char.get("m_leader_skill_id_sub_3"),
                char.get("additional_m_leader_skill_id_sub_3")
            ):
                return char
    
        return None
    
    def find_character_by_command_id(self, command_id:int):
        character_id = self.character_command_lookup.get(command_id)
        if character_id is None:
            return None
        return self.char_lookup.get(character_id)

    def safe_save_json(self, data, final_path):
        # Create a temporary file in the same directory
        dir_name = os.path.dirname(final_path)
        with tempfile.NamedTemporaryFile('w', encoding='utf8', delete=False, dir=dir_name, suffix='.tmp') as tmp:
            json.dump(data, tmp, ensure_ascii=False, indent=2)
            temp_path = tmp.name

        # Replace the original file with the temp file
        shutil.move(temp_path, final_path)

    def back_up_file(self, filename):
        masters_path = Path(Paths.GAME_MASTERS)
        source_file = masters_path / filename
        backup_path = Path(Paths.MASTERS_BACKUP)
        backup_file = backup_path / filename
        # Make sure the backup directory exists
        backup_file.parent.mkdir(parents=True, exist_ok=True)

        # Copy only if it hasn't already been backed up
        if not backup_file.exists():
            try:
                shutil.copy2(source_file, backup_file)
                print(f"            ├─ 🔒 Backed up Unity asset to: {backup_file}")
            except Exception as e:
                print(f"            ├─ ❌ Failed to back up {source_file}: {e}")