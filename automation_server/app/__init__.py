from flask import Flask
from flask_sqlalchemy import SQLAlchemy

import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(app.instance_path, 'app.sqlite')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Set up upload folder
    VOUCHER = os.path.join(os.getcwd(), 'vouchers')
    os.makedirs(VOUCHER, exist_ok=True)
    app.config['VOUCHER'] = VOUCHER

    IO_TRIP_SHEET = os.path.join(os.getcwd(), 'trip_sheet/io')
    os.makedirs(IO_TRIP_SHEET, exist_ok=True)
    app.config['IO_TRIP_SHEET'] = IO_TRIP_SHEET

    TRANSPORTER_TRIP_SHEET = os.path.join(os.getcwd(), 'trip_sheet/transporter')
    os.makedirs(TRANSPORTER_TRIP_SHEET, exist_ok=True)
    app.config['TRANSPORTER_TRIP_SHEET'] = TRANSPORTER_TRIP_SHEET

    TICKET = os.path.join(os.getcwd(), 'tickets')
    os.makedirs(TICKET, exist_ok=True)
    app.config['TICKET'] = TICKET

    db.init_app(app)

    with app.app_context():
        from .routes import bp as routes_bp
        from .models.trip import Trip, Ticket
        app.register_blueprint(routes_bp)
        db.create_all()

    return app

if __name__ == "__main__":
    # Create database and tables if not exist
    app = create_app()
    
    app.run(debug=True)
