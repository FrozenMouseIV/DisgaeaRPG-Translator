import io
import json
import os
from pathlib import Path
import shutil
import sys
import time
from typing import List
import UnityPy
from Code.config import Config, Paths


class UnityHelper:
    def __init__(self):
        self.env = UnityPy.load(Paths.GAME_MASTERS)
        self.masters_path = Path(Paths.GAME_MASTERS)        
        # Check if the folder exists and is not empty
        if not self.masters_path.is_dir():
            print(f" ❌ Error: The folder '{self.masters_path}' does not exist.")
            sys.exit(1)

        if not any(self.masters_path.iterdir()):
            print(f" ❌ Error: The folder '{self.masters_path}' is empty.")
            sys.exit(1)

        #Ensure required folders exist
        self.backup_path = Path(Paths.MASTERS_BACKUP)        
        self.backup_path.mkdir(parents=True, exist_ok=True)

        self.translation_source_path = Path(Paths.SOURCE_TRANSLATED_DIR)        
        self.translation_source_path.mkdir(parents=True, exist_ok=True)

        self.source_path = Path(Paths.SOURCE_DIR)        
        self.source_path.mkdir(parents=True, exist_ok=True)

        self.updated_files_path = Path(Paths.UPDATED_FILES_DIR)        
        self.updated_files_path.mkdir(parents=True, exist_ok=True)
        
        self.output_path = Path(Paths.TRANSLATED_FILES_DIR)        
        self.output_path.mkdir(parents=True, exist_ok=True)

        self.new_entries_path = Path(Paths.NEW_ENTRIES_DIR)        
        self.new_entries_path.mkdir(parents=True, exist_ok=True)

    # Initial datamine. Returns True if the initial setup was already done. False otherwise
    def initial_datamine(self) -> bool:
        """Extract only the missing JSON files from FILES_TO_TRANSLATE."""

        print(f"\n    ℹ️ Running initial setup")
        start_time = time.time()

        if Config.get_datetime_field(Config.INITIAL_SETUP):
            print("       ├─ ✅ Initial setup already completed.")
            return True

        print("       ├─ 🔁 Datamining game files...")
        for obj in self.env.objects:
            if obj.type.name != "MonoBehaviour":
                continue

            if not obj.serialized_type.nodes:
                continue

            data = obj.read()
            name = data.m_Name

            if name not in Config.FILES_TO_TRANSLATE and name != 'charactercommand':
                continue

            self._export_json(obj, name, self.updated_files_path)

            source_file = self.masters_path / name
            backup_file = self.backup_path / name
            # Make sure the backup directory exists
            backup_file.parent.mkdir(parents=True, exist_ok=True)

            # Copy only if it hasn't already been backed up
            if not backup_file.exists():
                try:
                    shutil.copy2(source_file, backup_file)
                    print(f"            ├─ 🔒 Backed up Unity asset to: {backup_file}")
                except Exception as e:
                    print(f"            ├─ ❌ Failed to back up {source_file}: {e}")
        
        end_time = time.time()
        elapsed = end_time - start_time
        print(f"       ├─ ✅ Completed initial setup in {elapsed:.2f}s.")
        return False

    # Datamine files specified on a list
    def datamine_files(self, files_to_datamine:list[str]) -> None:
        for obj in self.env.objects:
            if obj.type.name != "MonoBehaviour":
                continue

            if not obj.serialized_type.nodes:
                continue

            data = obj.read()
            name = data.m_Name

            # Datamine updated files and export to updated files folder
            if name in files_to_datamine and name in Config.FILES_TO_TRANSLATE:
                self._export_json(obj, name, Paths.UPDATED_FILES_DIR)
                source_file = self.masters_path / name
                backup_file = self.backup_path / name
                # Make sure the backup directory exists
                backup_file.parent.mkdir(parents=True, exist_ok=True)
                # Backup file (overwrite if if existed)
                shutil.copy2(source_file, backup_file)
                print(f"                 ├─  🔒 Backed up Unity asset to: {backup_file}")
  
    # Generate translated game files and place them in the Translated_Files folder
    def generate_translated_game_files(self, files_to_translate:List[str] = None) -> None:
        
        print(f"\n    ℹ️ Generating translated game files")
        start_time = time.time()

        # Delete before generating new files
        source_dir = Path(Paths.TRANSLATED_FILES_DIR)
        for file in source_dir.iterdir():
            if file.is_file():
                file.unlink()

        for obj in self.env.objects:
            if obj.type.name == "MonoBehaviour":
                filename = ''
                if obj.serialized_type.nodes:            
                    data = obj.read()
                    filename = data.m_Name
                    # If translating only updated files check if the file needs to be translated:
                    if files_to_translate is not None and filename not in files_to_translate: 
                        continue
                    # Check if the file is in the lit of files to translate
                    if filename not in Config.FILES_TO_TRANSLATE: 
                        continue
                    tree = obj.read_typetree()

                    updated = False
                    translated_data = self.__load_translated_data(filename)
                    translated_index = {entry["id"]: entry for entry in translated_data}

                    for item in tree['DataList']:
                        tid = item.get("id")
                        en_data = translated_index.get(tid)
                        if en_data is not None:
                            for key in Config.FIELDS_TO_TRANSLATE:
                                if key in en_data:
                                    item[key] = en_data[key]
                                    updated = True
                if updated:
                    obj.save_typetree(tree)
                    print(f"            ├─ 📦 Generated file: {filename}")

        for path, env_file in self.env.files.items():
            output_path = os.path.join(Paths.TRANSLATED_FILES_DIR, os.path.basename(path))
            filename = path[path.rfind('/') + 1:]
            if filename in Config.FILES_TO_TRANSLATE:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, "wb") as f:
                    f.write(env_file.save(packer=(64,2)))
        
        end_time = time.time()
        elapsed = end_time - start_time
        print(f"       ├─ ✅ Finished generating translated game files in {elapsed:.2f}s.")
 
    def __load_translated_data(self, filename:str):  
        filepath = os.path.join(Paths.SOURCE_TRANSLATED_DIR, filename + '.json')  
        with io.open(filepath, encoding='utf8') as fj:
            translated_source_data=json.load(fj)
            return translated_source_data
    
    def _export_json(self, obj, name: str, path=None) -> None:
        """Internal helper to write JSON to output folder."""

        if path is None:
            path = self.source_path

        if not isinstance(path, Path):
            path = Path(path)

        tree = obj.read_typetree()
        output_path = path / f"{name}.json"

        with open(output_path, "wt", encoding="utf8") as f:
            json.dump(tree['DataList'], f, ensure_ascii=False, indent=4)

        print(f"            ├─ 📝 Extracted: {name}")