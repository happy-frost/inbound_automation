import os
from pathlib import Path
from dotenv import load_dotenv

from flask import current_app
from selenium.common.exceptions import WebDriverException

from whatsapp_automation import Whatsapp

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

user_data_dir = os.getenv("USER_DATA_DIR")
profile_dir = os.getenv("PROFILE_DIRECTORY")

def get_whatsapp_service():
    # Check if already initialized
    if hasattr(current_app, 'whatsapp_service'):
        service = current_app.whatsapp_service
        try:
            # Try a harmless command to check if the driver is alive
            service.driver.title  # Will raise if browser is dead
            return service
        except WebDriverException:
            # Browser was closed; clean up and create a new one
            try:
                service.driver.quit()
            except Exception:
                pass  # Ignore further cleanup errors
            del current_app.whatsapp_service

    # Create a new Whatsapp service
    whatsapp = Whatsapp(user_data_dir, profile_dir)
    whatsapp.login()
    current_app.whatsapp_service = whatsapp
    return current_app.whatsapp_service