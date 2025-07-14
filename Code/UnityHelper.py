import io
import json
import os
from pathlib import Path
import shutil
from typing import List
import UnityPy
from Code.config import Config, Paths


class UnityHelper:
    def __init__(self):
        self.env = UnityPy.load(Paths.GAME_MASTERS)
        self.masters_path = Path(Paths.GAME_MASTERS)        
        self.masters_path.mkdir(parents=True, exist_ok=True)

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

    # Initial datamine. Returns True if the initial setup was already done. False otherwise
    def initial_datamine(self) -> bool:
        """Extract only the missing JSON files from FILES_TO_TRANSLATE."""

        print(f"    ℹ️ Running initial setup")

        existing_files = {f.stem for f in self.source_path.glob("*.json")}
        missing_files = set(Config.FILES_TO_TRANSLATE) - existing_files

        if Config.get_datetime_field(Config.INITIAL_SETUP) and not missing_files:
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

            if name in missing_files:
                self._export_json(obj, name)

                source_file = self.masters_path / name
                backup_file = self.backup_path / name
                # Make sure the backup directory exists
                backup_file.parent.mkdir(parents=True, exist_ok=True)

                # Copy only if it hasn't already been backed up
                if not backup_file.exists():
                    try:
                        shutil.copy2(source_file, backup_file)
                        print(f"            ├─ 📦 Backed up Unity asset to: {backup_file}")
                    except Exception as e:
                        print(f"            ├─ ❌ Failed to back up {source_file}: {e}")
        
        print("       ├─ ✅ Completed initial setup.")
        return False

    def datamine_files(self, files_to_datamine:list[str]) -> None:
        for obj in self.env.objects:
            if obj.type.name != "MonoBehaviour":
                continue

            if not obj.serialized_type.nodes:
                continue

            data = obj.read()
            name = data.m_Name

            if name in files_to_datamine:
                self._export_json(obj, name, Paths.UPDATED_FILES_DIR)
                backup_path = Path(Paths.MASTERS_BACKUP) / self.source_path.name
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                if not backup_path.exists():
                    shutil.copy2(self.source_path, backup_path)
                    print(f"📦 Backed up Unity asset to: {backup_path}")
        
        Config.set_datetime_field(Config.INITIAL_SETUP)
        return False
  
    def translate_game_files(self, files_to_translate:List[str] = None) -> None:
        for obj in self.env.objects:
            if obj.type.name == "MonoBehaviour":

                if obj.serialized_type.nodes:            
                    # save decoded data
                    data = obj.read()
                    #if data.m_Name in ignore:
                    if files_to_translate is None or data.m_Name in files_to_translate: 
                        print(f"Skipping file {data.m_Name}")
                        continue
                    tree = obj.read_typetree()

                    updated = False
                    translated_data = self.__load_translated_data(data.m_Name)
                    translated_index = {entry["id"]: entry for entry in translated_data}

                    for item in tree['DataList']:
                        tid = item.get("id")
                        en_data = translated_index.get(tid)
                        if en_data is not None:
                            for key in Config.FIELDS_TO_TRANSLATE:
                                if key in en_data:
                                    item[key] = en_data[key]
                                    updated = True
                    #data.save()
                if updated:
                    obj.save_typetree(tree)

        for path, env_file in self.env.files.items():
            output_path = os.path.join(Paths.SOURCE_TRANSLATED_DIR, os.path.basename(path))
            filename = path[path.rfind('/') + 1:]
            if filename in Config.FILES_TO_TRANSLATE:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, "wb") as f:
                    f.write(env_file.save(packer=(64,2)))
 
    def __load_translated_data(filename:str):  
        filepath = os.path.join(Paths.SOURCE_TRANSLATED_DIR, filename + '.json')  
        with io.open(filepath, encoding='utf8') as fj:
            translated_source_data=json.load(fj)
            return translated_source_data
    
    def _export_json(self, obj, name: str) -> None:
        """Internal helper to write JSON to output folder."""
        tree = obj.read_typetree()
        output_path = self.source_path / f"{name}.json"

        with open(output_path, "wt", encoding="utf8") as f:
            json.dump(tree['DataList'], f, ensure_ascii=False, indent=4)

        print(f"            ├─ 📝 Extracted: {name}")