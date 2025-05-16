import os
from pathlib import Path
from dotenv import load_dotenv

from sheets_automation.readSpreadsheet import ReadSpreadsheet

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
excel_name = os.getenv("EXCEL_NAME")

if __name__ == "__main__":
    spreadsheet = ReadSpreadsheet(excel_name)
    output = spreadsheet.get_A2C_tripsheet()