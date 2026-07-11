from flask import Blueprint, request, jsonify, render_template
from backend.models import db, User, Trek, Booking
from werkzeug.security import generate_password_hash, check_password_hash
from celery.result import AsyncResult
from backend.extensions import cache

api = Blueprint('trekking_api_unique', __name__)

@api.route('/')
def index():
    return render_template('index.html')

@api.route('/login', methods=['GET','POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()
    
    if user and check_password_hash(user.password_hash, data['password']):
        return jsonify({
            "message": "Login Successful", 
            "username": user.username, 
            "role": user.role, 
            "id" : user.id
        }), 200
    return jsonify({"error": "Invalid credentials"}), 401

@api.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    hashed_pw = generate_password_hash(data['password'])
    
    # Check if user already exists
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "User already exists"}), 400
        
    new_user = User(username=username, password_hash=hashed_pw,role='Trekker', status='Active')
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "Registration Successful"}), 201

@api.route('/dashboard/<username>', methods=['GET'])
def get_dashboard(username):
    print("DEBUG: Fetching dashboard for:", username)
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    # 1. Sare treks fetch karein
    all_treks = Trek.query.all()
    trek_list = [{"id": t.id, "title": t.name, "slots": t.slots} for t in all_treks]

    # 2. IS USER KI BOOKINGS FETCH KAREIN 
    user_bookings = Booking.query.filter_by(user_id=user.id).all()
    booking_list = []
    for b in user_bookings:
        # Trek table se uska naam dhundhein
        trek_obj = Trek.query.get(b.trek_id) 
        trek_name = trek_obj.name if trek_obj else "Unknown"
        booking_list.append({"id": b.id, "trek_name": trek_name, "status": b.status})
        
    # 3. Dono return karein
    return jsonify({
        "user": {"username": user.username},
        "treks": trek_list,
        "bookings": booking_list  
    }), 200

@api.route('/book-trek', methods=['POST'])
def book_trek():
    data = request.get_json()
    print("DEBUG: Received Data =", data)
    username = data.get('username')
    trek_id = data.get('trek_id')

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    trek = Trek.query.get(trek_id)
    if not trek or trek.available_slots <= 0:
        return jsonify({"error": "No slots left!"}), 400

    # 1. Booking add karo
    new_booking = Booking(user_id=user.id, trek_id=trek_id,trek_name=trek.name,username=user.username)
    db.session.add(new_booking)
    
    # 2. Slots kam karo
    trek.available_slots -= 1
    
    # 3. COMMIT yahan likhein (If block ke bahar)
    db.session.commit()
    
    return jsonify({"message": "Trek Booked Successfully!"}), 200  

@api.route('/my-bookings/<username>', methods=['GET'])
def get_my_bookings(username):
    user = User.query.filter_by(username=username).first()
    bookings = Booking.query.filter_by(user_id=user.id).all()
    booking_list = [{"id": b.id,"trek_name": b.trek_name, "status": b.status} for b in bookings]
    return jsonify({"bookings": booking_list}), 200

@api.route('/treks', methods=['GET'])
@cache.cached(timeout=300)
def get_treks():
    treks = Trek.query.all()
    return jsonify([{
        'id': t.id, 
        'name': t.name, 
        'location': t.location, 
        'difficulty': t.difficulty,
        'available_slots': t.available_slots 
    } for t in treks])


@api.route('/trek/create', methods=['POST'])
def create_trek():
    data = request.get_json()
    new_trek = Trek(
        name=data['name'],
        location=data['location'],
        difficulty=data['difficulty'],
        duration=data['duration'],
        slots=data['slots'],
        available_slots=data['slots'], 
        start_date=data['start_date'],
        end_date=data['end_date']
    )
    db.session.add(new_trek)
    db.session.commit()
    return jsonify({"message": "Trek Created Successfully!"}), 201


@api.route('/admin/toggle-blacklist/<int:user_id>', methods=['POST'])
def toggle_blacklist(user_id):
    user = User.query.get(user_id)
    if user:
        user.is_blacklisted = not user.is_blacklisted
        db.session.commit()
        return jsonify({"message": "User status updated", "is_blacklisted": user.is_blacklisted})
    return jsonify({"error": "User not found"}), 404

@api.route('/admin/add-staff', methods=['POST'])
def add_staff():
    data = request.get_json()
    
    new_staff = User(
        username=data['username'],
        password_hash=generate_password_hash(data['password']),
        role='Staff',
        status='Active'
    )
    
    db.session.add(new_staff)
    db.session.commit()
    
    return jsonify({"message": "Staff created successfully"}), 201


@api.route('/admin/assign-staff/<int:trek_id>', methods=['POST'])
def assign_staff(trek_id):
    data = request.get_json()
    trek = Trek.query.get(trek_id)
    if trek:
        trek.assigned_staff_id = data['staff_id']
        db.session.commit()
        return jsonify({"message": "Staff assigned successfully"}), 200
    return jsonify({"error": "Trek not found"}), 404

@api.route('/staffs', methods=['GET'])
def get_staffs():
    staffs = User.query.filter_by(role='Staff').all()
    return jsonify([{'id': s.id, 'username': s.username} for s in staffs])

@api.route('/staff/my-treks/<int:staff_id>', methods=['GET'])
def get_staff_treks(staff_id):
    treks = Trek.query.filter_by(assigned_staff_id=staff_id).all()
    return jsonify([{'id': t.id, 'name': t.name, 'status': t.status} for t in treks])

@api.route('/treks/open', methods=['GET'])
def get_open_treks():
    treks = Trek.query.filter_by(status='Open').all()
    return jsonify([{'id': t.id, 'name': t.name, 'location': t.location} for t in treks])

@api.route('/cancel-booking/<int:booking_id>', methods=['DELETE'])
def cancel_booking(booking_id):
    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({"message": "Booking not found"}), 404
    
    trek = Trek.query.get(booking.trek_id)
    if trek:
        trek.available_slots += 1
    
    db.session.delete(booking)
    db.session.commit()
    return jsonify({"message": "Cancelled successfully"}), 200

@api.route('/staff/complete-trek/<int:trek_id>', methods=['POST'])
def complete_trek(trek_id):
    trek = Trek.query.get(trek_id)
    if not trek:
        return jsonify({"message": "Trek not found"}), 404
    
    trek.status = 'Completed'
    db.session.commit()
    return jsonify({"message": "Trek marked as completed"}), 200


@api.route('/export-csv', methods=['POST'])
def trigger_csv():
    print("Button click hua!")
    try:
        from backend.tasks import export_bookings_to_csv
        task = export_bookings_to_csv.delay() # Celery ka task trigger hoga
        print(f"Task ID:{task.id}")
        return {"message": "Task queued", "task_id": task.id}, 202
    except Exception as e:
        print(f"ASLI ERROR YE HAI: {e}")
        return {"error": str(e)}, 500
    
@api.route('/treks/search', methods=['GET'])
def search_treks():
    location = request.args.get('location', '').strip()
    difficulty = request.args.get('difficulty', '').strip()

    print(f"DEBUG: Searching for Loc: '{location}', Diff: '{difficulty}'")
    
    query = Trek.query
    if location:
        query = query.filter(Trek.location.ilike(f'%{location}%'))
    if difficulty:
        query = query.filter(Trek.difficulty.ilike(f'%{difficulty}%'))
        
    treks = query.all()
    print(f"Found {len(treks)} treks for location: {location}, diff: {difficulty}")
    return jsonify([{'id': t.id, 'name': t.name, 'location': t.location, 'difficulty': t.difficulty, 'available_slots': t.available_slots} for t in treks])


@api.route('/booking/update-status/<int:booking_id>', methods=['POST'])
def update_booking_status(booking_id):
    data = request.get_json()
    new_status = data.get('status') 
    
    booking = Booking.query.get(booking_id)
    if not booking:
        return jsonify({"error": "Booking not found"}), 404
        
    booking.status = new_status
    db.session.commit()
    return jsonify({"message": f"Booking {new_status} successfully"}), 200


@api.route('/user/stats/<int:user_id>', methods=['GET'])
def get_user_stats(user_id):
    total_bookings = Booking.query.filter_by(user_id=user_id).count()
    completed_bookings = Booking.query.filter_by(user_id=user_id, status='Completed').count()
    
    return jsonify({
        "total_bookings": total_bookings,
        "completed_bookings": completed_bookings
    }), 200


@api.route('/admin/users', methods=['GET'])
def get_users():
    users = User.query.filter(User.role != 'Admin').all() 
    return jsonify([{'id': u.id, 'username': u.username, 'is_blacklisted': u.is_blacklisted} for u in users])