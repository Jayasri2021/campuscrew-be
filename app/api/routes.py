from flask import Blueprint, request, jsonify
from app.models import Users, Services
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