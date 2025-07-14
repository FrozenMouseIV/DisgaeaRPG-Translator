import time
from Code.TranslationUtil import Translator_Util
from Code.UnityHelper import UnityHelper
from Code.config import Config

def main():

    start_time = time.time()
    
    print(f"Started execution")
    #STEP 1 - DATAMINE GAME FILES   
    unity_helper = UnityHelper()
    initial_setup_done = unity_helper.initial_datamine()

    #STEP 2 - TRANSLATE FILES

    translator_helper = Translator_Util()
    # 2 - 1: INITIAL SETUP NEEDED. PATCH EVERYTHING FROM SOURCE_TRANSLATED
    if initial_setup_done == False:
        translator_helper.initial_translation()
        unity_helper.generate_translated_game_files()

    # 2 - 2: INITIAL SETUP ALREADY DONE. LOOK FOR UPDATED FILES
    else:       
        translator_helper.find_updated_files() # look for updated files
        translator_helper.translate_updated_files() # translate them
        unity_helper.generate_translated_game_files(Config.get_updated_files())

    # STEP 3 - MOVE FILES TO MASTERS FOLDER?
    translator_helper.update_game_files()
    if initial_setup_done == False:
        Config.set_datetime_field(Config.INITIAL_SETUP)
    Config.set_datetime_field(Config.LAST_EXECUTION)
    
    end_time = time.time()
    elapsed = end_time - start_time
    print(f"✅ Finished execution in {elapsed:.2f}s")


if __name__ == "__main__":
    main()