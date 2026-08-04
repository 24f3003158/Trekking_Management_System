from celery_config import celery
from backend import create_app


import csv
import io

@celery.task
def export_bookings_to_csv():
    from backend.models import Booking
    app=create_app()
    with app.app_context():
        bookings = Booking.query.all()
        
        # CSV file memory mein banane ke liye
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'User', 'Trek', 'Status']) # Headers
        
        for b in bookings:
            writer.writerow([b.id, b.user_id, b.trek_id, b.status])
            
        return output.getvalue()


@celery.task
def send_daily_reminder(user_email, trek_name):
    from backend.models import Booking, User
    app=create_app()
    with app.app_context():
        bookings=Booking.query.all()

        for b in bookings:
            user=User.query.get(b.user_id)
            if user and user.email:
                print(f"Daily Remainder: Hello {user.username}, don't forget your upcoming trek!")
        
        return "daily reminders sent successfully!"