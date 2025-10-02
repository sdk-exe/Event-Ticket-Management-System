# ticketdatabase.py

from app import app, db, Ticket

def main():
    with app.app_context():
        tickets = Ticket.query.all()
        for ticket in tickets:
            print(f"Ticket ID: {ticket.id}, Attendee Name: {ticket.attendee_name}, Valid: {ticket.is_valid}")

if __name__ == "__main__":
    main()
