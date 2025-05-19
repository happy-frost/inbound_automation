import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import json

import gspread
import pandas as pd
from datetime import datetime, timedelta
from oauth2client.service_account import ServiceAccountCredentials

def get_exe_dir():
    if getattr(sys, 'frozen', False):
        # If running from a PyInstaller bundle
        return Path(sys.executable).parent
    else:
        # If running from source
        return Path(__file__).resolve().parent.parent

# Use the correct runtime path for .env
env_path = get_exe_dir() / ".env"
load_dotenv(dotenv_path=env_path)

json_key = os.getenv("JSON_KEY")

# Setup credentials
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(json_key, scope)
client = gspread.authorize(creds)

class ReadSpreadsheet:
    def __init__(self,spreadsheet_name:str):
        '''
        Initialize the 
        input: name of the spreadsheet file
        '''
        self.spreadsheet = client.open(spreadsheet_name)
        try: 
            with open("data.json", "r") as f:
                data = json.load(f)
                self.sic_offset = data["sic_offset"]
                self.pvt_offset = data["pvt_offset"]
        except:
            data = {"sic_offset": 2, "pvt_offset": 2}
            with open("data.json", "w") as f:
                json.dump(data, f)

            self.sic_offset = data["sic_offset"]
            self.pvt_offset = data["pvt_offset"]

        
    def get_A2C_tripsheet(self,date:str="tomorrow",folder:str=''):
        '''
        Function that takes the date and returns the excel file of trip sheet ot be sent to A2C for that particular date
        input: 
            date in this string format (2025-05-01) default value is tomorrow
            folder path to save the excel file to
        output: tuple (Boolean,String) The first value is if there is at least 1 transfer on the date, the second value is the path to the excel file
        '''
        if date == "tomorrow":
            date = (datetime.today() + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0) # set time to 00:00:00 to fit pandas default
            output_name = datetime.strftime(date,"%Y-%m-%d A2C Trip Sheet.xlsx")
            sic_offset = self.sic_offset
            pvt_offset = self.pvt_offset
        else:
            try:
                datetime.strptime(date,"%Y-%m-%d")
            except:
                print("Incorrect date string format, please format it like this 'YYYY-MM-DD' (i.e. 2025-05-01)")
            output_name = f"{date} A2C Trip Sheet.xlsx"
            sic_offset = 2
            pvt_offset = 2
        
        target_date = pd.to_datetime(date)
        current_year = datetime.now().year
        
        # Open the Google Sheet by name
        sic_worksheet = self.spreadsheet.worksheet(f"{current_year} SIC")
        pvt_worksheet = self.spreadsheet.worksheet(f"{current_year} PVT")

        # Get data from Row after offset
        headers = sic_worksheet .row_values(1)
        data_rows = sic_worksheet.get(f"A{sic_offset}:N")
        records = [dict(zip(headers, row)) for row in data_rows]
        sic_df = pd.DataFrame(records)

        headers = pvt_worksheet .row_values(1)
        data_rows = pvt_worksheet.get(f"A{pvt_offset}:N")
        records = [dict(zip(headers, row)) for row in data_rows]
        pvt_df = pd.DataFrame(records)

        # Ensure date column is parsed as datetime
        sic_df['Date'] = pd.to_datetime(sic_df['Date'])
        pvt_df['Date'] = pd.to_datetime(pvt_df['Date'])

        # Filter by a specific date and supplier is A2C
        filtered_sic_df = sic_df[(sic_df['Date'] == target_date) & (sic_df['Supplier'] == "A2C")]
        filtered_sic_df = filtered_sic_df.drop(columns=['Travel Agent', 'Supplier']) 
        filtered_pvt_df = pvt_df[(pvt_df['Date'] == target_date) & (pvt_df['Supplier'] == "A2C")]
        filtered_pvt_df = filtered_pvt_df.drop(columns=['Travel Agent', 'Supplier'])

        if not filtered_sic_df.empty:
            sic_offset = filtered_sic_df.index[-1] + 3
        if not filtered_pvt_df.empty:
            pvt_offset = filtered_pvt_df.index[-1] + 3
    
        # only move offset for tomorrow queries, otherwise a query for future value will affect tomorrow query
        # offset is meant to make tomorrow queries more efficient
        if date == "tomorrow": 
            self.update_offset(max(sic_offset,self.sic_offset),max(pvt_offset,self.pvt_offset))

        # put the SIC and PVT transfer together and sort by time (string sort works since it is using 24 hour time format)
        output_df = pd.concat([filtered_sic_df, filtered_pvt_df],ignore_index=True)
        output_df['Date'] = output_df['Date'].dt.date
        output_df.sort_values(by="Time",inplace=True)

        if not os.path.exists(folder):           
            os.makedirs(folder)
        
        output_path = os.path.join(folder,output_name)
        if not output_df.empty:
            output_df.to_excel(output_path, index=False)
            return (True, output_path)
        else:
            return (False,"")
    
    def update_offset(self,sic_offset:int,pvt_offset:int):
        data = {"sic_offset": sic_offset, "pvt_offset": pvt_offset}
        with open("data.json", "w") as f:
            json.dump(data, f)