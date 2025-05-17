# Sheets Automation

This module is to automate the process of reading from a google spreadsheet, and preparing an excel to be sent.

## 📚 Features

- Reads from google spreadsheet
- Concat relevant data from multiple worksheets
- Make changes to the data accordingly removing fields that are nott o be sent
- Send the excel with whatsapp

## 🛠️ Setup
### Requirements
- Python 3.7+
- Google Chrome + ChromeDriver
- Selenium
- whatsapp_automation library

### Install dependencies

```bash
pip install selenium pandas oauth2client gspread dotenv
```

### Preparing env
Copy the sample.env to a .env file and add the necessary information.

