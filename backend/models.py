from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    _tablename_ = 'user' # Double underscore use karein
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False) 
    status = db.Column(db.String(20), default='Active') 
    contact_details = db.Column(db.String(200), nullable=True)
    is_blacklisted = db.Column(db.Boolean, default=False)

class Trek(db.Model):
    _tablename_ = 'treks' # Double underscore use karein
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(150), nullable=False)
    difficulty = db.Column(db.String(20), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    available_slots = db.Column(db.Integer, default=0)
    assigned_staff_id = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(20), default='Open')
    start_date = db.Column(db.String(50), nullable=False)
    end_date = db.Column(db.String(50), nullable=False)
    slots = db.Column(db.Integer, default=0)
    
    # ADDITION: Relationship ke liye helper field (koi purana code break nahi hoga)
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "location": self.location,
            "difficulty": self.difficulty,
            "status": self.status
        }

class Booking(db.Model):
    _tablename_ = 'bookings' # Double underscore use karein
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String(80), nullable=False)
    trek_id = db.Column(db.Integer, nullable=False)
    trek_name = db.Column(db.String(150), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Booked')
    
    _table_args_ = (db.UniqueConstraint('user_id', 'trek_id', name='_user_trek_uc'),)