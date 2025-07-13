from datetime import datetime
import json
import os
from pathlib import Path
from typing import List, Optional

class Config:

    DEEPL_API_KEY = "YOUR API KEY HERE"
    INITIAL_SETUP = "initial_setup_date"
    LAST_EXECUTION = "last_execution_date"

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
    def get_date_field(cls, field_name: str) -> Optional[datetime]:
        """Get a datetime field from the config by name."""
        config = cls._load_config()
        date_str = config.get(field_name)
        if date_str:
            try:
                # Parse ISO 8601 format
                return datetime.fromisoformat(date_str.rstrip("Z"))
            except ValueError:
                print(f"⚠️ Failed to parse datetime field '{field_name}': {date_str}")
        return None

    @classmethod
    def set_datetime_field(cls, field_name: str, dt: Optional[datetime] = None):
        """Set a datetime field in the config using local time."""
        config = cls._load_config()
        dt_str = (dt or datetime.now()).isoformat()  # Local time
        config[field_name] = dt_str
        cls._save_config(config)

    @classmethod
    def set_updated_files(cls, updated_files: List[str]):
        config = cls._load_config()
        config['updated_files'] = updated_files
        cls._save_config(config)

    @classmethod
    def get_updated_files(cls) -> List[str]:
        config = cls._load_config()
        return config.get('updated_files', [])
        
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

    FILES_TO_IGNORE = ['areareward', 'banner', 'campaign', 'campaignloginbonus', 
            'characterboost', 'charactermagiccommand', 'charactercommand', 'charactermaterial', 'characterretrofit',
            'divisionbattle', 'divisionbattlehpreducereward', 'divisionbattlerankingreward', 'divisionbattlereward',
            'divisionbattlerewardgroup', 'divisionbattlestage', 
            'enemy', 'enemygroupposition', 'enemyleaderskill', 
            'eventboostcharacter', 'eventterm',
            'gacha', 'gachabonus', 'gachabonuscategory', 'gachabonusgroup', 'gachabutton', 'gachagroup', 'gachagroupitem', 
            'gachalot', 'gachapickup', 'gachaspecificcountbonus', 'gachaspecificprice',
            'itemshop', 'mapeventbattlerankingreward', 'mapeventbattlereward', 'mapeventbattlerewardgroup',
            'memorystory',
            'product', 'productpresent', 'renewstoryeventboss', 'ritualtrainingmaterialdata', 'ritualtrainingstage',
            'stageenemygroup', 'story', 'storycharacter', 'storytalk', 'stopnotificationterm'
          ]

    FILES_TO_CHECK_FOR_UPDATES =  ['command', 'leaderskill']

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
    MASTERS_BACKUP = "/Masters_Backup"
    GAME_MASTERS = os.path.join(
        os.getenv("LOCALAPPDATA").replace("Local", "LocalLow"),
        "disgaearpg",
        "DisgaeaRPG",
        "assetbundle",
        "masters"
    )