from datetime import datetime
import json
import os
import shutil
import time
from Code.UnityHelper import UnityHelper
from Code.config import Config, Paths
from Code.Translator import Translator

class Translator_Util:
    
    def __init__(self):
        self.translator = Translator()

    def __translate_file(self, filename):
        print(f"       ├─ 🔁 Translating file {filename}.")
        source_path = os.path.join(Paths.SOURCE_DIR, f'{filename}')
        out_path = os.path.join(Paths.SOURCE_TRANSLATED_DIR, f'{filename}')
        temp_path = out_path + '.tmp'

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
                print("⚠️ Couldn't decode existing output file. Starting from scratch.")

        # Track already translated IDs to skip
        translated_ids = {entry["id"] for entry in translated_data}

        count = 0
        for entry in jp_data:
            if entry["id"] in translated_ids:
                continue

            merged = entry.copy()
            for key in Config.FIELDS_TO_TRANSLATE:
                if key in merged and merged[key] != '':
                    translated = self.translator.translate(filename, key, merged[key])
                    merged[key] = translated

            translated_data.append(merged)
            count += 1

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

        print(f"            ├─ 📝 Done: {len(translated_data)} total entries written to {out_path}")

    # in case the initial files are not up to date. Look for new entries, translate and update our translations
    def initial_translation(self):
        print(f"    ℹ️ Running initial translation")
        for filename in os.listdir(Paths.SOURCE_DIR):
            file_path = os.path.join(Paths.SOURCE_DIR, filename)
            # Skip subfolders
            if not os.path.isfile(file_path):
                continue
            self.__translate_file(filename=filename)
        print("       ├─ ✅ Completed initial setup.")

    # Look for files changed after last execution
    def find_updated_files(self):
        # Get last run time so we can look for updated files
        timestamp = Config.get_date_field(Config.LAST_EXECUTION)
        if timestamp is None:
            timestamp = Config.get_date_field(Config.INITIAL_SETUP)

        #Reset config
        updated_files = []
        Config.set_updated_files(updated_files)

        # 🔁 Walk through all files in the folder
        for filename in os.listdir(Paths.SOURCE_DIR):
            file_path = os.path.join(Paths.SOURCE_DIR, filename)

            # Skip subfolders
            if not os.path.isfile(file_path):
                continue

            # Get last modified time
            mtime = os.path.getmtime(file_path)
            modified_date = datetime.fromtimestamp(mtime)

            # Compare with cutoff date
            if modified_date > timestamp:
                updated_files.append(filename)
                # 🔒 Make a backup
                if filename in Config.FILES_TO_TRANSLATE:
                    backup_path = os.path.join(Paths.MASTERS_BACKUP, filename)
                    shutil.copy2(file_path, backup_path)
                    print(f"🧱 Backed up: {filename} → {backup_path}")

        # 🖨️ Print or use the list
        print("Files updated after", timestamp.strftime("%Y-%m-%d %H:%M:%S"))
        for f in updated_files:
            print(f)

        unity_helper = UnityHelper()
        unity_helper.datamine_files(updated_files)   
        Config.set_updated_files(updated_files)   

    # translate updated files
    def translate_updated_files(self):
        for filename in os.listdir(Paths.UPDATED_FILES_DIR):
            file_path = os.path.join(Paths.UPDATED_FILES_DIR, filename)
            name_only = os.path.splitext(filename)[0]

            # Skip subfolders
            if not os.path.isfile(file_path):
                continue

            if name_only in Config.FILES_TO_TRANSLATE:
                start_time = time.time()
                print(f"🔄 Processing: {name_only}...")
                # Call your translation method
                self.__translate_file(name_only)
                end_time = time.time()
                elapsed = end_time - start_time
                print(f"✅ Finished: {name_only} in {elapsed:.2f}s")

                if name_only not in Config.FILES_TO_CHECK_FOR_UPDATES:
                    os.remove(file_path)     