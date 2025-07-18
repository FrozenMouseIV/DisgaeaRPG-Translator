from datetime import datetime
import json
import os
from pathlib import Path
import shutil
import time
from typing import Any
from Code.Helper import Helper
from Code.UnityHelper import UnityHelper
from Code.config import Config, Paths
from Code.Translator import Translator

class Translator_Util:
    
    def __init__(self):
        self.translator = Translator()
        self.helper = Helper()

    def __translate_file(self, filename:str, path:str):
        print(f"       ├─ 🔁 Translating file {filename}.")
        start_time = time.time()
        source_path = os.path.join(path, f'{filename}')
        out_path = os.path.join(Paths.SOURCE_TRANSLATED_DIR, f'{filename}')
        temp_path = out_path + '.tmp'
        
        name_only = os.path.splitext(filename)[0]
        new_entries_path = os.path.join(Paths.NEW_ENTRIES_DIR, f"{name_only}_new_entries.json")

        # Load JP source (list of entries)
        with open(source_path, 'r', encoding='utf8') as f:
            jp_data = json.load(f)

        # Load existing translated data if any (resume support)
        translated_data = []
        if os.path.exists(out_path):
            try:
                with open(out_path, 'r', encoding='utf8') as f:
                    translated_data = json.load(f)
            except json.JSONDecodeError:
                print("            ├─ ⚠️ Couldn't decode existing output file. Starting from scratch.")

        # Track already translated IDs to skip
        translated_ids = {entry["id"] for entry in translated_data}

        count = 0
        new_count = 0
        new_entries = []
        for entry in jp_data:
            count += 1
            if entry["id"] in translated_ids:
                continue

            merged = entry.copy()
            for key in Config.FIELDS_TO_TRANSLATE:
                if key in merged and merged[key] != '':
                    translated = self.translator.translate(filename, key, merged[key])
                    merged[key] = translated

            translated_data.append(merged)
            new_entries.append(merged) #track additions
            new_count += 1

            # Periodic save every 100 entries
            if count % 100 == 0:
                try:
                    with open(temp_path, 'w', encoding='utf8') as f:
                        json.dump(translated_data, f, ensure_ascii=False, indent=2)
                    shutil.move(temp_path, out_path)
                except Exception as e:
                    print(f"            ├─ ❌ Error writing progress: {e}")
                    if os.path.exists(temp_path):
                        print(f"            ├─ ⚠️ Temp file preserved at: {temp_path}")

        # Final save
        with open(out_path, 'w', encoding='utf8') as f:
            json.dump(translated_data, f, ensure_ascii=False, indent=2)

        # Save just the new entries to a separate file
        if new_entries and name_only in Config.FILES_TO_TRACK_NEW_ENTRIES:
            with open(new_entries_path, 'w', encoding='utf8') as f:
                json.dump(new_entries, f, ensure_ascii=False, indent=2)

        end_time = time.time()
        elapsed = end_time - start_time
        print(f"            ├─ 📝 Finished translating file {filename}: {len(translated_data)} total entries written to {out_path} in {elapsed:.2f}s")
        if new_count > 0:
            print(f"                ├─ 🛠️ Added {new_count} new lines to the file")

    def __translate_file_changes(self, source_data:dict[Any, Any], updated_data:dict[Any, Any], filename):
        print(f"       ├─ 🔁 Checking {filename} for updates.")
        start_time = time.time()

        # Load existing translated data
        out_path = os.path.join(Paths.SOURCE_TRANSLATED_DIR, f'{filename}.json')  
        if os.path.exists(out_path):
            with open(out_path, 'r', encoding='utf8') as f:
                translated_data = {entry["id"]: entry for entry in json.load(f)}
        else:
            translated_data = {}
        updated_count = 0
        updated_translated_data = []
        updated_character_ids = []

        for id_, old_entry in source_data.items():
            if id_ not in updated_data:
                continue  # Entry was removed in JP (unlikely, but safe check)

            new_entry = updated_data[id_]
            translated_entry = translated_data.get(id_, new_entry.copy())

            for field in Config.FIELDS_TO_CHECK_FOR_UPDATES:
                if field in new_entry:
                    old_value = old_entry.get(field)
                    new_value = new_entry.get(field)

                    if old_value != new_value:

                        if filename == "leaderskill":
                            char = self.helper.find_character_by_leaderskill_id(new_entry['id'])
                            if char is not None:
                                if char['id'] not in updated_character_ids:
                                    updated_character_ids.append(char['id'])
                            char_name = 'N/A' if char is None else char['name']
                            print(f"            ├─ ℹ️  Updating Evility {translated_entry['name']} with ID: {id_} for Character: {char_name}")

                        elif filename == "command":
                            char = self.helper.find_character_by_command_id(new_entry['id'])
                            if char is not None:
                                if char['id'] not in updated_character_ids:
                                    updated_character_ids.append(char['id'])
                            char_name = 'N/A' if char is None else char['name']
                            print(f"            ├─ ℹ️  Updating Skill {translated_entry['name']} with ID: {id_} for Character: {char_name}")                     

                        print(f"                ├─ Old Value: {translated_entry[field]}")
                        translated_text = self.translator.translate(filename=filename, field=field, value=new_value)
                        if translated_text:
                            translated_entry[field] = translated_text
                            print(f"                ├─ New Value: {translated_text}")
                            updated_count += 1
                            entry_updated = True
                        else:
                            print(f"⚠️ No translation for ID {id_} field '{field}': {new_value}")                   


            updated_translated_data.append(translated_entry)

        # Save updated translation file
        out_path = os.path.join(Paths.SOURCE_TRANSLATED_DIR, f'{filename}.json')
        self.helper.safe_save_json(updated_translated_data, out_path)

        end_time = time.time()
        elapsed = end_time - start_time
        print(f"            ├─ 🛠️ Finihed checking {filename}: {updated_count} entries updated in {elapsed:.2f}s")
 
    # in case the initial files are not up to date. Look for new entries, translate and update our translations
    def initial_translation(self):
        print(f"\n    ℹ️ Running initial translation")
        start_time = time.time()
        for filename in os.listdir(Paths.UPDATED_FILES_DIR):
            file_path = os.path.join(Paths.UPDATED_FILES_DIR, filename)
            # Skip subfolders
            if not os.path.isfile(file_path):
                continue
            self.__translate_file(filename=filename, path=Paths.UPDATED_FILES_DIR)

            ## Keep leaderkill and command files on source folder
            ## They become the new source to compare against on future updates
            if filename in Config.FILES_TO_CHECK_FOR_UPDATES:
                destination_path = os.path.join(Paths.SOURCE_DIR, filename)
                shutil.copy2(file_path, destination_path)  # use shutil.move if you want to move instead
            elif filename != 'charactercommand':
                os.remove(file_path)  # delete the file if not in KEEP_FILES

        end_time = time.time()
        elapsed = end_time - start_time
        print(f"       ├─ ✅ Completed initial translation in {elapsed:.2f}s.")

    # Look for files changed after last execution
    def find_updated_files(self):     
        # Get last run time so we can look for updated files
        timestamp = Config.get_datetime_field(Config.LAST_EXECUTION)
        if timestamp is None:
            timestamp = Config.get_datetime_field(Config.INITIAL_SETUP)

        print(f"\n    ℹ️  Looking for files updated after {timestamp.strftime("%Y-%m-%d %H:%M:%S")}")
        start_time = time.time()

        #Reset config
        updated_files = []
        Config.set_updated_files(updated_files)

        # 🔁 Walk through all files in the masters folder
        for filename in os.listdir(Paths.GAME_MASTERS):
            file_path = os.path.join(Paths.GAME_MASTERS, filename)

            # Skip subfolders
            if not os.path.isfile(file_path):
                continue

            # Get last modified time
            mtime = os.path.getmtime(file_path)
            modified_date = datetime.fromtimestamp(mtime)

            # Compare with cutoff date
            if modified_date > timestamp:
                updated_files.append(filename)

        # 🖨️ Print or use the list
        print("            ├─  🔁 Files updated since last execution:")
        for f in updated_files:
            print(f"                 ├─  📦 {f}")

        unity_helper = UnityHelper()
        unity_helper.datamine_files(updated_files)   
        Config.set_updated_files(updated_files)

        end_time = time.time()
        elapsed = end_time - start_time
        print(f"       ├─ ✅ Finished looking for updated files in {elapsed:.2f}s.")   

    # translate updated files
    def translate_updated_files(self):

        print(f"\n    ℹ️  Translating updated files")
        start_time = time.time()

        for filename in os.listdir(Paths.UPDATED_FILES_DIR):
            file_path = os.path.join(Paths.UPDATED_FILES_DIR, filename)
            name_only = os.path.splitext(filename)[0]

            # Skip subfolders
            if not os.path.isfile(file_path):
                continue

            if name_only in Config.FILES_TO_TRANSLATE:
                self.__translate_file(filename, path=Paths.UPDATED_FILES_DIR)

                if name_only not in Config.FILES_TO_CHECK_FOR_UPDATES:
                    os.remove(file_path)   

        end_time = time.time()
        elapsed = end_time - start_time
        print(f"       ├─ ✅ Finished translating updated files in {elapsed:.2f}s.")  

    def find_and_translate_file_changes(self):

        print(f"\n    ℹ️  Looking for character updates")
        start_time = time.time()

        for updated_file in os.listdir(Paths.UPDATED_FILES_DIR):
            updated_file_path = os.path.join(Paths.UPDATED_FILES_DIR, updated_file)
            updated_file_name = os.path.splitext(updated_file)[0]

            original_file_path = os.path.join(Paths.SOURCE_DIR, updated_file)

            # Skip subfolders
            if not os.path.isfile(original_file_path):
                continue

            if updated_file_name in Config.FILES_TO_CHECK_FOR_UPDATES:

                # Load updated data
                with open(updated_file_path, 'r', encoding='utf8') as f:
                    updated_data = {entry["id"]: entry for entry in json.load(f)}

                # Load source data
                with open(original_file_path, 'r', encoding='utf8') as f:
                    source_data = {entry["id"]: entry for entry in json.load(f)}

                self.__translate_file_changes(source_data=source_data, updated_data=updated_data, filename=updated_file_name)

            # Move files to source for the next update
            destination_folder = Paths.SOURCE_DIR
            os.makedirs(destination_folder, exist_ok=True)
            destination_path = os.path.join(destination_folder, f'{updated_file_name}.json')
            # Move the file
            shutil.move(updated_file_path, destination_path)

        end_time = time.time()
        elapsed = end_time - start_time
        print(f"       ├─ ✅ Finished looking for character updates in {elapsed:.2f}s.")  

    def update_game_files(self):
        print(f"\n    ℹ️ Updating game files")
        source_dir = Path(Paths.TRANSLATED_FILES_DIR)
        target_dir = Path(Paths.GAME_MASTERS)

        # Ensure the destination exists
        target_dir.mkdir(parents=True, exist_ok=True)

        # Copy all files (ignoring subdirectories)
        for file in source_dir.iterdir():
            if file.is_file():
                target_file = target_dir / file.name
                shutil.copy2(file, target_file)
                print(f"       ├─ 🔁 Copied {file.name} to {target_file}")
        print("   ├─ ✅ Finished updating game files.")