# Event-Ticket-Management-System
### Author: Shaurya Deepak Khemka

## Overview
This is a complete, production-ready event management system built to handle ticketing digitally.
The system solves a critical event management problem: how to issue unique, fraud-proof tickets and validate them quickly at the door. It features a Flask web backend that generates encrypted QR-coded tickets, a local SQLite database for speed and redundancy, and real-time synchronization with a Google Sheet for easy access by the organizing team.

## Features
* Unique Ticket Generation: Creates tickets with a unique ID and an encrypted QR code.
* Real-Time Scanning: A dedicated scanner page uses a device's camera to read QR codes.
* Instant Validation: The system instantly verifies if a ticket is valid and has not already been used.
* Fraud Prevention: Marks tickets as "used" in the database upon successful entry, preventing duplicate use.
* Google Sheets Sync: All ticket information (attendee name, ticket ID, status) is synced in real-time to a shared Google Sheet.
* Local Database: Uses Flask-SQLAlchemy with a SQLite database for fast, local data management.

## System Architecture
1. Ticket Generation: An admin enters attendee details on the main page. The Flask backend creates a new entry in the local tickets.db, generates a unique QR code containing an encrypted ticket ID, and saves it as an image.
2. Scanning: At the event, staff access the /scan endpoint on a mobile device. The page uses HTML5 and JavaScript to access the camera.
3. Validation: Upon scanning a QR code, the data is sent to the Flask backend. The backend decrypts the ticket ID, checks its status in the database, and updates it to "Used."
4. Sync: The validation result is simultaneously updated in the designated Google Sheet via the Google Sheets API.

## Repository Structure

	.
 	├── app.py                  # Main Flask application, routes, and logic
	├── requirements.txt
	├── .gitignore
	├── templates/
	│   ├── index.html          # Main page for generating tickets
	│   ├── scan.html           # Page for scanning QR codes
	|── static/                 # Directory where generated QR codes are saved
	|    └── (OR Codes)  '
	├──init_db.py
	├──ticketdatabase.py
	└──reset_database.py
	
## Setup & Usage Instructions

1. Clone the Repository

		git clone https://github.com/sdk-exe/Event-Ticket-Management-System.git
		cd Event-Ticket-Management-System

2. Set Up a Virtual Environment

		# Create the environment
		python -m venv venv

		# Activate it
		# Windows
		venv\Scripts\activate
		# macOS/Linux
		source venv/bin/activate

3. Install Dependencies

		pip install -r requirements.txt

4. Configure Google Cloud Credentials
This application requires a Google Cloud Service Account to interact with Google Sheets.

		1. Follow the Google Cloud documentation to create a service account.
		2. Enable the "Google Sheets API" and "Google Drive API" for your project.
		3. Download the service account's JSON key file.
		4. IMPORTANT: Rename the file to service_account.json and place it in the project's root directory. The .gitignore file is already configured to prevent this file from being uploaded to GitHub.
		5. Share your target Google Sheet with the client_email found inside your service_account.json file.
   		6. Replace the placeholders for SHEET_ID and SERVICE_ACCOUNT_FILE inside app.py with your own Sheet ID and Service Account File.

6. Initialize the Database
Run the database initialization script. This only needs to be done once.

		python init_db.py

7. Run the Application

		python app.py

- The application will be running at http://127.0.0.1:5000.
- To create a record with it QR code, you can enter the name of the atendee in the locally hosted application.
- The QR code will be stored in the folder named [Static](static), the record will be reflected in the datase and synced to the Google Sheet in real time.
- To scan the QR code, open the HTML document named [scan.html](templates/scan.html) situated in the templates folder and start scanning using a webcam.
- Scans will automatically be reflected in the database and synced to the Google Sheet in real time.

## Utilities

1. To initialize the database

		python init_db.py

2. To view all existing records in database locally

		python ticketdatabase.py

3. To reset database

		python reset_database.py

## License
This project is licensed under the MIT License. See the [LICENSE](LICENCE) file for details.
