from flask import Blueprint, request, jsonify
from app.models import Users, Services, Bookings
import uuid

api = Blueprint('api', __name__)

@api.route('/createUser', methods=['POST'])
def create_user():
    data = request.get_json()
    firstName = data.get('firstName')
    lastName = data.get('lastName')
    email = data.get('email')
    password = data.get('password')
    isPfw = data.get("isPfw")
    if not password or not email:
        return jsonify({'error': 'E-Mail and password are required'}), 400
    
    existing_user = Users.find_by_email(email)
    if existing_user:
        return jsonify({'error': 'Email is already in use'}), 400

    user_id = str(uuid.uuid1())
    new_user, error = Users.create_user(email, password, firstName, lastName, user_id, is_pfw= isPfw)
    if error:
        return jsonify({'error': error}), 500

    return jsonify({'message': 'User created successfully', 'user_id': user_id, 'first_name': firstName, 'lastName': lastName, 'email':email, 'isPfw': isPfw}), 201


@api.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'E-Mail and password are required'}), 400

    user = Users.find_by_email(email)
    
    if user is None:
        return jsonify({'error': 'User not found'}), 400
    
    if user and Users.check_password(user, password):
        return jsonify({'message': 'Login successful', 'user_id': user["user_id"],  'first_name': user["first_name"], 'lastName': user["last_name"], 'email': user["email"],  'is_pfw': user["is_pfw"]}), 200
    else:
        return jsonify({'error': 'Invalid email or password'}), 400

@api.route("/createService", methods=["POST"])
def create_service():
    try:
        data = request.get_json()
        name = data.get("name")
        description = data.get("description")
        rate = data.get("rate")
        category_id = data.get("category_id")
        user_id = data.get("user_id") 
        image_urls = data.get("image_urls", [])
        availability = data.get("availability", []) 

        if not all([name, description, rate, category_id, user_id]):
            return jsonify({"error": "Missing required fields"}), 400

        service_id, error = Services.create_service(name, description, rate, category_id, user_id)
        if error:
            return jsonify({"error": error}), 500

        if image_urls:
            images, error = Services.add_service_images(service_id, image_urls)
            if error:
                return jsonify({"error": error}), 500

        if availability:
            availability_data, error = Services.add_availability_slots(service_id, availability)
            if error:
                return jsonify({"error": error}), 500

        return jsonify({
            "message": "Service created successfully",
            "service_id": service_id
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route("/fetchService", methods=["GET"])
def get_services():
    try:
        category_id = request.args.get('category_id')
        user_id = request.args.get('user_id')
        if category_id:
            services, error = Services.get_services_by_category(category_id)
            if error:
                return jsonify({"error": error}), 500
            return jsonify({
                "message": "Services fetched successfully",
                "services": services,
                "filter": "category",
                "category_id": category_id
            }), 200
            
        elif user_id:
            services, error = Services.get_services_by_user(user_id)
            if error:
                return jsonify({"error": error}), 500
            return jsonify({
                "message": "Services fetched successfully",
                "services": services,
                "filter": "user",
                "user_id": user_id
            }), 200
            
        else:
            services, error = Services.get_all_services()
            if error:
                return jsonify({"error": error}), 500
            return jsonify({
                "message": "Services fetched successfully",
                "services": services,
                "filter": "none"
            }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@api.route("/createBooking", methods=["POST"])
def create_booking():
    try:
        data = request.get_json()
        service_id = data.get("service_id")
        user_id = data.get("user_id")
        start_time = data.get("start_time")
        end_time = data.get("end_time")

        if not all([service_id, user_id, start_time, end_time]):
            return jsonify({"error": "Missing required fields"}), 400

        booking, error = Bookings.create_booking(service_id, user_id, start_time, end_time)
        
        if error:
            return jsonify({"error": error}), 400

        return jsonify({
            "message": "Booking created successfully",
            "booking": {
                "booking_id": booking["booking_id"],
                "slot_id": booking["slot_id"],
                "booked_by": booking["booked_by"],
                "booking_time": booking["booking_time"]
            }
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route("/bookings/<user_id>", methods=["GET"])
def get_user_bookings(user_id):
    try:
        bookings, error = Bookings.get_user_bookings(user_id)
        if error:
            return jsonify({"error": error}), 500

        return jsonify({
            "message": "Bookings fetched successfully",
            "bookings": bookings
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route("/booking/slot/<slot_id>", methods=["GET"])
def get_booking_by_slot(slot_id):
    try:
        booking, error = Bookings.get_booking_by_slot(slot_id)
        if error:
            return jsonify({"error": error}), 500

        return jsonify({
            "message": "Booking fetched successfully",
            "booking": booking
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
