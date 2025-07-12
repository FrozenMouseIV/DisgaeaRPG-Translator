# config.py

# TRANSLATOR API KEYS
import os

class Config:
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
