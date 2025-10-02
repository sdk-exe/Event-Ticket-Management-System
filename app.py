# app.py

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import qrcode
import uuid
import os
import gspread
from google.oauth2.service_account import Credentials
import logging
import re

app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tickets.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize Database
db = SQLAlchemy(app)

# Setup Logging
if not os.path.exists('logs'):
    os.mkdir('logs')
file_handler = logging.FileHandler('logs/ticketing.log')
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
file_handler.setFormatter(formatter)
app.logger.addHandler(file_handler)

# Google Sheets Configuration
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SERVICE_ACCOUNT_FILE = 'dandiyatickets-6a90ec20ce71.json'  # Ensure this file is in your project directory

credentials = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=SCOPES
)

gc = gspread.authorize(credentials)

SHEET_ID = '1O6qOmn3ZYbYVZejgmZYKE3xROFsWGxVNnSLKRa_YZ5o'  # Replace with your actual Google Sheet ID
sh = gc.open_by_key(SHEET_ID)
worksheet = sh.sheet1  # Assumes you're using the first sheet

# Database Model
class Ticket(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    attendee_name = db.Column(db.String(100), nullable=False)
    is_valid = db.Column(db.Boolean, default=True)

# Helper function to sanitize filenames
def sanitize_filename(name):
    """
    Sanitize the attendee's name to create a safe filename.
    - Converts to lowercase
    - Replaces spaces with underscores
    - Removes non-alphanumeric characters except underscores
    """
    name = name.lower()
    name = name.replace(' ', '_')
    name = re.sub(r'[^a-z0-9_]', '', name)
    return name

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_ticket', methods=['POST'])
def generate_ticket():
    try:
        name = request.form.get('attendee_name', '').strip()
        if not name:
            app.logger.warning("No attendee name provided.")
            return jsonify({"status": "error", "message": "Attendee name cannot be empty."}), 400

        ticket_id = str(uuid.uuid4())
        new_ticket = Ticket(id=ticket_id, attendee_name=name)
        db.session.add(new_ticket)
        db.session.commit()

        # Generate QR Code
        qr = qrcode.make(ticket_id)

        # Sanitize attendee name for filename
        sanitized_name = sanitize_filename(name)
        # Ensure 'static' directory exists
        static_dir = os.path.join(app.root_path, 'static')
        os.makedirs(static_dir, exist_ok=True)

        # Create a unique filename with attendee name and ticket_id
        qr_filename = f"{sanitized_name}_{ticket_id}.png"
        qr_path = os.path.join(static_dir, qr_filename)
        qr.save(qr_path)

        # Append data to Google Sheet
        worksheet.append_row([ticket_id, name, True])

        app.logger.info(f"Generated ticket {ticket_id} for attendee '{name}' with QR code '{qr_filename}'.")

        return jsonify({"ticket_id": ticket_id, "qr_code": f'qr_code/{qr_filename}'}), 200
    except Exception as e:
        db.session.rollback()  # Rollback in case of error
        app.logger.error(f"Error generating ticket: {e}")
        return jsonify({"status": "error", "message": "An unexpected error occurred. Please try again later."}), 500

@app.route('/qr_code/<filename>', methods=['GET'])
def serve_qr_code(filename):
    try:
        static_dir = os.path.join(app.root_path, 'static')
        return send_from_directory(static_dir, filename)
    except FileNotFoundError:
        app.logger.warning(f"QR Code file {filename} not found.")
        return jsonify({"status": "error", "message": "QR Code not found."}), 404

@app.route('/scan', methods=['GET'])
def scan():
    return render_template('scan.html')

@app.route('/scan_ticket', methods=['POST'])
def scan_ticket():
    try:
        data = request.get_json()
        ticket_id = data.get('ticket_id', '').strip()

        if not ticket_id:
            app.logger.warning("No ticket ID provided for scanning.")
            return jsonify({"status": "error", "message": "No ticket ID provided."}), 400

        ticket = Ticket.query.get(ticket_id)
        if ticket and ticket.is_valid:
            ticket.is_valid = False  # Mark as used
            db.session.commit()

            # Update Google Sheet: Find the row with the ticket_id and update 'Is Valid' to False
            try:
                cell = worksheet.find(ticket_id)
                if cell:
                    worksheet.update_cell(cell.row, 3, False)
                    app.logger.info(f"Ticket {ticket_id} validated and marked as used in Google Sheet.")
                else:
                    app.logger.warning(f"Ticket ID {ticket_id} not found in Google Sheet.")
            except gspread.exceptions.CellNotFound:
                app.logger.warning(f"Ticket ID {ticket_id} not found in Google Sheet during update.")

            app.logger.info(f"Ticket {ticket_id} validated and marked as used in database.")
            return jsonify({"status": "valid", "message": "Ticket validated!"}), 200
        else:
            app.logger.warning(f"Invalid or already used ticket attempt: {ticket_id}.")
            return jsonify({"status": "invalid", "message": "Ticket is invalid or already used."}), 400
    except Exception as e:
        app.logger.error(f"Error scanning ticket: {e}")
        return jsonify({"status": "error", "message": "An unexpected error occurred. Please try again later."}), 500

# Global error handler
@app.errorhandler(Exception)
def handle_exception(e):
    """Handle all uncaught exceptions."""
    app.logger.error(f"Unhandled exception: {e}", exc_info=True)
    return jsonify({
        "status": "error",
        "message": "An unexpected error occurred. Please try again later."
    }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
