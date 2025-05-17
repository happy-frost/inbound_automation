import time
import os
from pathlib import Path
from dotenv import load_dotenv

from whatsapp_automation import Whatsapp

from sheets_automation.readSpreadsheet import ReadSpreadsheet

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
excel_name = os.getenv("EXCEL_NAME")
user_data_dir = os.getenv("USER_DATA_DIR")
profile_directory = os.getenv("PROFILE_DIRECTORY")
whatsapp_chat = os.getenv("WHATSAPP_CHAT")

if __name__ == "__main__":
    try:
        spreadsheet = ReadSpreadsheet(excel_name)
        hasTripsheet, path = spreadsheet.get_A2C_tripsheet(folder="A2C Trip Sheet")
        full_path = os.path.normpath(os.path.join(Path(__file__).parent,path))

        whatsapp = Whatsapp(user_data_dir,profile_directory)
        whatsapp.login()
        whatsapp.go_to_chat(whatsapp_chat)

        if hasTripsheet:
            whatsapp.send_document(full_path,"Tripsheet for tomorrow")
        else:
            whatsapp.send_message("No tripsheet for tomorrow")
        time.sleep(10)
    except Exception as e:
        print(e)
