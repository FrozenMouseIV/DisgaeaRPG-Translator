from Code.TranslationUtil import Translator_Util
from Code.UnityHelper import UnityHelper
from Code.config import Config

def main():
    #STEP 1 - DATAMINE GAME FILES   
    unity_helper = UnityHelper()
    initial_setup_done = unity_helper.initial_datamine()

    #STEP 2 - TRANSLATE FILES

    translator_helper = Translator_Util()
    # 2 - 1: INITIAL SETUP NEEDED. PATCH EVERYTHING FROM SOURCE_TRANSLATED
    if initial_setup_done == False:
        translator_helper.initial_translation()
        unity_helper.translate_game_files(Config.get_updated_files())

    # 2 - 2: INITIAL SETUP ALREADY DONE. LOOK FOR UPDATED FILES
    else:       
        translator_helper.find_updated_files() # look for updated files
        translator_helper.translate_updated_files() # translate them
        unity_helper.translate_game_files(Config.get_updated_files())

    # STEP 3 - MOVE FILES TO MASTERS FOLDER?

if __name__ == "__main__":
    main()