import os
from werkzeug.utils import secure_filename
from flask import Blueprint, request, request, redirect, url_for, render_template, current_app
from sqlalchemy import func
from datetime import date, datetime
from .models.trip import Trip, Ticket
from .utils.transfer_message import Customer_Tranfer, get_customer_transfers
from . import db 

bp = Blueprint('routes', __name__)

upload_bp = Blueprint('upload', __name__, template_folder='../templates')

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

@bp.route('/send-trip-sheet', methods=['POST'])
def send_trip_sheet():
    uploaded_file = request.files.get('input_file')
    if not uploaded_file:
        return "No file uploaded", 400

    # save file
    filename = secure_filename(uploaded_file.filename)
    upload_folder = current_app.config['TRANSPORTER_TRIP_SHEET']
    file_path = os.path.join(upload_folder, filename)
    uploaded_file.save(file_path)

    # get customer transfers from transporter trip sheet
    customer_transfer = get_customer_transfers(file_path)
    if not customer_transfer:
        return "failed"
    missing_trip = []
    message = []
    for customer in customer_transfer:
        trip = Trip.query.filter(
        func.lower(Trip.guest_name) == func.lower(customer.guest_name),
        func.date(Trip.start_date) <= func.date(customer.date),
        func.date(Trip.end_date) >= func.date(customer.date)).all()
        if not trip:
            missing_trip.append(customer.guest_name)
        else:
            print("go to whatsapp chat:",trip[0].whatsapp_group_id)
            print("send whatsapp message:",customer.output_message())
        message.append(customer.output_message())
        
    if missing_trip:
        out = "Missing trip:\n" + '\n'.join(missing_trip)
        return out
    return "success"

