from celery_config import celery
import csv
import io

@celery.task
def export_bookings_to_csv():
    from backend.models import Booking
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
    print(f"Reminder sent to {user_email} for trek: {trek_name}")
    return True