import datetime
import json
import os
from pathlib import Path

class Config:

    @classmethod
    def _load_config(cls):
        if cls.CONFIG_PATH.exists():
            with cls.CONFIG_PATH.open("r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    @classmethod
    def _save_config(cls, config: dict):
        with cls.CONFIG_PATH.open("w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)

    @classmethod
    def get_last_execution_date(cls) -> str | None:
        config = cls._load_config()
        return config.get("lastexecutiondate")

    @classmethod
    def update_last_execution_date(cls, date: datetime = None):
        config = cls._load_config()
        date_str = (date or datetime.today()).strftime("%Y-%m-%d")
        config["lastexecutiondate"] = date_str
        cls._save_config(config)
        
    DEEPL_API_KEY = "YOUR API KEY HERE"
    FILES_TO_TRANSLATE =  [
        'achievement', 'agenda', 'area', 'arenacategory', 'beginnermission',
        'charactermission', 'character', 'characterclassname', 'characterintroduction',
        'command', 
        'customdailymission', 'custommonthlymission', 'custompartskind', 'customtotalmission', 
        'drink', 'drinkskill', 
        'episode', 
        'equipment', 'equipmenteffecttype', 
        'eventmission', 'eventmissiondaily', 'eventmissionrepetition', 
        'help', 'hospital', 
        'innocent', 'innocentrecipe',
        'item', 'iteminformation', 
        'kingdomrank', 'leaderskill', 'liqueur', 
        'memory', 'memoryeffecttype', 'museum', 'potentialclass', 'product', 'ritualtrainings',
        'stage', 'stagemission', 'survey', 'tower', 
        'travelbenefit', 'travelnegativeeffect', 
        'trophy', 'trophydaily', 'trophydailyrequest', 'trophyrepetition', 'trophyweekly', 
        'weapon'
    ]

    FIELDS_TO_TRANSLATE = [
        'ability_description', 'body', 'category', 'class_name', 'class_name_1',
        'class_name_2', 'class_name_3', 'class_name_4', 'class_name_5',
        'description', 'description_effect', 'description_format',
        'get_areas', 'name', 'name_battle', 'release_content_description',
        'resource_name', 'title'
    ]

class Paths:
    CONFIG_PATH = Path("config.json")
    SOURCE_DIR = "/Source"
    SOURCE_TRANSLATED_DIR = "/Source_Translated"
    TRANSLATED_FILES_DIR = "/Translated_Files"
    UPDATED_FILES_DIR = "/Updated_Files"
    GAME_MASTERS = os.path.join(
        os.getenv("LOCALAPPDATA").replace("Local", "LocalLow"),
        "disgaearpg",
        "DisgaeaRPG",
        "assetbundle",
        "masters"
    )
