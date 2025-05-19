# Sheets Automation

This module is to automate the process of reading from a google spreadsheet, and preparing an excel to be sent.

## 📚 Features

- Reads from google spreadsheet
- Concat relevant data from multiple worksheets
- Make changes to the data accordingly removing fields that are not to be sent
- Send the excel with whatsapp

## 🛠️ Setup
### Requirements
- Python 3.7+
- Google Chrome + ChromeDriver
- Selenium
- pandas
- whatsapp_automation library

### Install dependencies
```bash
pip install selenium pandas oauth2client gspread dotenv
```
Clone whatsapp_automation library from https://github.com/happy-frost/whatsapp_automation

### Preparing env
Copy the sample.env to a .env file and add the necessary information.

