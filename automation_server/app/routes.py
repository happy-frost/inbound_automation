import os
import time
from random import randint

from pathlib import Path
from dotenv import load_dotenv

from werkzeug.utils import secure_filename
from flask import Blueprint, request, request, redirect, url_for, render_template, current_app
from sqlalchemy import func

from datetime import date, datetime
from .models.trip import Trip, Ticket
from .utils.transfer_message import Customer_Tranfer, get_customer_transfers
from .utils.whatsapp_service import get_whatsapp_service
from . import db 

bp = Blueprint('routes', __name__)

upload_bp = Blueprint('upload', __name__, template_folder='../templates')

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

source_folder = os.getenv("SOURCE_FOLDER")
transporter_group_id = os.getenv("TRANSPORTER_CHAT_GROUP_ID")

@bp.route('/')
def index():
    upcoming_trips = Trip.query.filter(
        func.date(Trip.start_date) > func.date(date.today())).all()
    ongoing_trips = Trip.query.filter(
        func.date(Trip.end_date) >= func.date(date.today()),
        func.date(Trip.start_date) <= func.date(date.today())
        ).all()
    
    return render_template('index.html', ongoing_trips=ongoing_trips, upcoming_trips=upcoming_trips)


@bp.route('/past-trips')
def past_trips():
    past_trips = Trip.query.filter(
        func.date(Trip.end_date) < func.date(date.today())).all()
    return render_template('past_trips.html', past_trips=past_trips)

@bp.route('/add-docx',methods=['POST'])
def add_trip_with_docx():
    uploaded_file = request.files.get('input_file')
    if not uploaded_file:
        return "No file uploaded", 400

    filename = secure_filename(uploaded_file.filename)
    upload_folder = current_app.config['VOUCHER']
    file_path = os.path.join(upload_folder, filename)
    uploaded_file.save(file_path)

    # Add file
    new_trip = Trip()
    new_trip.populate_with_docx(file_path)
    same_trip = Trip.query.filter(
        func.lower(Trip.guest_name) == func.lower(new_trip.guest_name),
        func.date(Trip.start_date) == func.date(new_trip.start_date), 
        func.date(Trip.end_date) == func.date(new_trip.end_date)).all()
    if len(same_trip) == 0:    
        db.session.add(new_trip)
        db.session.commit()
        return "Trip added!", 201
    else: 
        return "Trip exists!", 200

@bp.route('/add-manually', methods=['GET', 'POST'])
def add_trip_manually():
    if request.method == 'POST':
        # User submits trip manually
        start_date = datetime.strptime(request.form['start_date'][:10],'%Y-%m-%d')
        end_date = datetime.strptime(request.form['end_date'][:10],'%Y-%m-%d')
        
        new_trip = Trip()

        new_trip.populate_manually(request.form['guest_name'],request.form['adults'],request.form['children'],request.form['children_below_six'],[],start_date,end_date)
        db.session.add(new_trip)
        db.session.commit()
        return redirect(url_for('routes.trip',trip_id=new_trip.id))
    return render_template("add_trip.html")

@bp.route('/add-ticket/<int:trip_id>',methods=['POST'])
def add_ticket(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    if not trip:
        return "Trip not found"
    
    uploaded_file = request.files.getlist('input_file')

    if not uploaded_file:
        return "No file uploaded", 400
    
    for file in uploaded_file:
        filepath = file.filename  # This includes the folder path from client
        newfilepath = trip.guest_name + '/' + '/'.join(filepath.split("/")[1:]) # add tickets with root file name as guest_name accoridng to trip id
        upload_folder = current_app.config['TICKET']
        file_path = os.path.join(upload_folder, newfilepath)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        file.save(file_path)

    return 'Folder uploaded successfully!'

@bp.route('/delete-trip/<int:trip_id>', methods=['POST'])
def delete_trip(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    db.session.delete(trip)
    db.session.commit()
    return "success"

@bp.route('/whatsapp_group_id/<int:trip_id>', methods=['GET', 'POST'])
def whatsapp_group_id(trip_id):
    # Fetch the trip by ID
    trip = Trip.query.get_or_404(trip_id)
    
    # Check if today's date is greater than or equal to the end_date
    if request.method == 'POST':
        # User submits feedback
        trip.whatsapp_group_id = request.form['group_id']
        db.session.commit()
        return redirect(url_for('routes.trip', trip_id=trip.id))
    
    # If it's the correct time, render a form for the user to fill in feedback
    return render_template('request_whatsapp_group_id.html', trip=trip)

@bp.route('/trip/<int:trip_id>', methods=['GET', 'POST'])
def trip(trip_id):
    trip = Trip.query.get_or_404(trip_id)
    return render_template('trip.html', trip=trip)

@bp.route('/send-trip-sheet')
def send_trip_sheet():
    try:
        whatsapp = get_whatsapp_service()
        
        target_file_name = "ODY" + datetime.strftime(datetime.now(),"%Y%m%d") + ".xlsx"
        destination_folder = os.path.join(os.getcwd(), "trip_sheet/transporter")

        isSuccess = whatsapp.go_to_chat(transporter_group_id)
        if not isSuccess:
            return "Cannot find chat"
        hasTodayTripSheet = whatsapp.find_file(target_file_name,source_folder,destination_folder)
        if not hasTodayTripSheet:
            return "No trip sheet for today"
        
        file_path = os.path.join(destination_folder,target_file_name)
        # get customer transfers from transporter trip sheet
        customer_transfers = get_customer_transfers(file_path)

        if not customer_transfers:
            return "failed"
        errors = {}
        for customer in customer_transfers:
            trip = Trip.query.filter(
            func.lower(Trip.guest_name) == func.lower(customer.guest_name),
            func.date(Trip.start_date) <= func.date(customer.date),
            func.date(Trip.end_date) >= func.date(customer.date)).all()
            if not trip:
                errors["missing_trip"] = errors.get("missing_trip",[]) + [customer.guest_name]
            elif not trip[0].whatsapp_group_id:
                errors["missing_whatsapp_group_id"] = errors.get("missing_whatsapp_group_id",[]) + [customer.guest_name]
            else:
                goToChat = whatsapp.go_to_chat(trip[0].whatsapp_group_id)
                sentMessage = whatsapp.send_message(customer.output_message())
                if not goToChat or not sentMessage:
                    errors["error_sending_message"] = errors.get("sending_message",[]) + [customer.guest_name]

            
            # Send tickets
            # Find the tickets for the day
            ticket_folder = current_app.config['TICKET']
            path1 = os.path.join(ticket_folder, customer.guest_name)
            path2 = os.path.join(path1, datetime.strftime(customer.date,"%d %b %Y"))

            if not os.path.isdir(path1):
                # if no ticket file
                continue
            
            if not os.path.isdir(path2):
                # if not ticket for today
                continue
            
            # Get all files (not directories) inside the second folder
            files = [f for f in os.listdir(path2) if os.path.isfile(os.path.join(path2, f))]
            for filename in files:
                filepath = os.path.join(path2,filename)
                sentTickets = whatsapp.send_document(filepath)
                time.sleep(randint(3,6))
                if not sentTickets:
                    errors["error_sending_ticket"] = errors.get("sending_message",[]) + [filename]
                
        if len(errors) != 0:
            out = []
            for error, customer_name in errors.items():
                out.append(f'<p>{error}: {customer_name}</p>')
            return ''.join(out)
        
        return "success"
    except:
        return "An error occurred"

@bp.route('/whatsapp/login')
def whatsapp_login():
    try:
        whatsapp = get_whatsapp_service()
        return "Successfully logged in to whatsapp"
    except:
        return "an error occurred"
