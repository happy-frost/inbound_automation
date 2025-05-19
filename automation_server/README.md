# Automation Server

This module creates a webserver and a HTML page to interact with the server.

## 📚 Features
- Upload new trips based on voucher
- Manually upload trip (information required: Guest name and number of adults/children)
- Take input of the group id with guests
- Read from the chat with transporter and find today's trip sheet
- Send the transfer informations to client

## 🛠️ Setup
### Requirements
- Python 3.7+
- Google Chrome + ChromeDriver
- Selenium
- whatsapp_automation library
- docx
- pandas

### Install dependencies
```bash
pip install selenium pandas docx
```
Clone whatsapp_automation library from https://github.com/happy-frost/whatsapp_automation

### Preparing env
Copy the sample.env to a .env file and add the necessary information.