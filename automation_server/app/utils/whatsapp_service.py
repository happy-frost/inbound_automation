from whatsapp_automation import Whatsapp
from flask import current_app


def get_whatsapp_service():
    if not hasattr(current_app, 'whatsapp_service'):
        current_app.whatsapp_service = Whatsapp()
    return current_app.whatsapp_service