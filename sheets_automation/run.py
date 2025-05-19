import time
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

sys.path.append(str(Path(__file__).resolve().parent))

from whatsapp_automation import Whatsapp

from read_spreadsheet.readSpreadsheet import ReadSpreadsheet

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

excel_name = os.getenv("EXCEL_NAME")
user_data_dir = os.getenv("USER_DATA_DIR")
profile_directory = os.getenv("PROFILE_DIRECTORY")
whatsapp_chat = os.getenv("WHATSAPP_CHAT")

if __name__ == "__main__":
    try:
        spreadsheet = ReadSpreadsheet(excel_name)
        hasTripsheet, path = spreadsheet.get_A2C_tripsheet(folder="Trip Sheet For Transporter")
        full_path = os.path.normpath(os.path.join(Path(__file__).parent,path))

        whatsapp = Whatsapp(user_data_dir,profile_directory)
        whatsapp.login()
        whatsapp.go_to_chat(whatsapp_chat)

        if hasTripsheet:
            success = whatsapp.send_document(full_path,"Tripsheet for tomorrow")
            if success:
                os.remove(full_path)
        else:
            whatsapp.send_message("No tripsheet for tomorrow")
        time.sleep(10)
    except Exception as e:
        print(e)
