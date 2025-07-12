
import json
from pathlib import Path
import UnityPy
from config import Config, Paths


class UnityHelper:
    def __init__(self, source_path: Path = Paths.GAME_MASTERS, output_dir: Path = Paths.SOURCE_DIR):
        self.source_path = source_path
        self.output_dir = output_dir
        self.env = UnityPy.load(source_path)

        # Ensure the output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)


    def initial_datamine(self):
        """Extract only the missing JSON files from FILES_TO_TRANSLATE."""
        existing_files = {f.stem for f in self.output_dir.glob("*.json")}
        missing_files = Config.FILES_TO_TRANSLATE - existing_files

        if not missing_files:
            print("✅ All target files are already extracted.")
            return

        for obj in self.env.objects:
            if obj.type.name != "MonoBehaviour":
                continue

            if not obj.serialized_type.nodes:
                continue

            data = obj.read()
            name = data.m_Name

            if name in missing_files:
                self._export_json(obj, name)

    def _export_json(self, obj, name: str):
        """Internal helper to write JSON to output folder."""
        tree = obj.read_typetree()
        output_path = self.output_dir / f"{name}.json"

        with open(output_path, "wt", encoding="utf8") as f:
            json.dump(tree['DataList'], f, ensure_ascii=False, indent=4)

        print(f"📝 Extracted: {name}")
