from werkzeug.security import generate_password_hash, check_password_hash
from .config import Config
from supabase import create_client
import uuid
from datetime import datetime

supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)

class Users:
    @staticmethod
    def create_user(email, password, first_name, last_name, user_id, is_pfw):
        hashed_password = generate_password_hash(password)
        response = supabase.table("users").insert({
            "email": email,
            "password": hashed_password,
            "first_name": first_name,
            "last_name": last_name,
            "user_id": user_id,
            "is_pfw": is_pfw
        }).execute()
        print(response)
        if not response.data:
            return None, f"Failed to create user: {response.data}"
        return response.data, None

    @staticmethod
    def find_by_email(email):
        response = supabase.table("users").select("*").eq("email", email).execute()
        if not response or len(response.data) == 0:
            return None
        return response.data[0]

    @staticmethod
    def check_password(user, password):
        return check_password_hash(user["password"], password)

class Services:
    @staticmethod
    def create_service(name, description, rate, category_id, user_id):
        service_id = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat()
        response = supabase.table("services").insert({
            "service_id": service_id,
            "name": name,
            "description": description,
            "rate": rate,
            "user_id": user_id,
            "category_id": category_id,
            "created_at": created_at
        }).execute()

        if not response.data:
            return None, f"Failed to create service: {response.error.message if response.error else 'Unknown error'}"
        return service_id, None

    @staticmethod
    def add_service_images(service_id, image_urls):
        image_records = [{"service_id": service_id, "image_url": url} for url in image_urls]
        response = supabase.table("serviceimages").insert(image_records).execute()

        if not response.data:
            return None, f"Failed to add service images: {response.error.message if response.error else 'Unknown error'}"
        return response.data, None

    @staticmethod
    def add_availability_slots(service_id, availability):
        slot_records = [
            {
                "service_id": service_id,
                "day_of_week": slot["day_of_week"],
                "start_time": slot["start_time"],
                "end_time": slot["end_time"]
            }
            for slot in availability
        ]
        response = supabase.table("serviceavailability").insert(slot_records).execute()

        if not response.data:
            return None, f"Failed to add service availability: {response.error.message if response.error else 'Unknown error'}"
        return response.data, None
    
    @staticmethod
    def get_all_services():
        try:
            response = supabase.table("services") \
                .select("*, serviceimages(image_url), serviceavailability(day_of_week, start_time, end_time), users!inner(first_name, last_name, email)") \
                .execute()
            
            if not response.data:
                return [], None
            
            return response.data, None
        except Exception as e:
            return None, f"Error fetching services: {str(e)}"
        

    @staticmethod
    def get_services_by_category(category_id):
        try:
            response = supabase.table("services") \
                .select("*, serviceimages(image_url), serviceavailability(day_of_week, start_time, end_time), users!inner(first_name, last_name, email)") \
                .eq("category_id", category_id) \
                .execute()
            
            if not response.data:
                return [], None
                
            return response.data, None
        except Exception as e:
            return None, f"Error fetching services by category: {str(e)}"
        
    @staticmethod
    def get_services_by_user(user_id):
        try:
            response = supabase.table("services") \
                .select("*, serviceimages(image_url), serviceavailability(day_of_week, start_time, end_time), users!inner(first_name, last_name, email)") \
                .eq("user_id", user_id) \
                .execute()
            
            if not response.data:
                return [], None
                
            return response.data, None
        except Exception as e:
            return None, f"Error fetching services by user: {str(e)}"
class Bookings:
    @staticmethod
    def create_slot(service_id, start_time, end_time):
        try:
            slot_id = int(datetime.utcnow().timestamp() * 1000)
            
            slot_response = supabase.table("slots").insert({
                "slot_id": slot_id,
                "service_id": service_id,
                "start_time": start_time,
                "end_time": end_time,
                "is_booked": False
            }).execute()

            if not slot_response.data:
                return None, "Failed to create slot"

            return slot_response.data[0], None
        except Exception as e:
            return None, str(e)

    @staticmethod
    def create_booking(service_id, user_id, start_time, end_time):
        try:
            slot, error = Bookings.create_slot(service_id, start_time, end_time)
            if error:
                return None, error

            booking_id = str(uuid.uuid4())
            
            response = supabase.table("bookings").insert({
                "booking_id": booking_id,
                "slot_id": slot["slot_id"],
                "booked_by": user_id,
                "booking_time": datetime.utcnow().isoformat()
            }).execute()

            if not response.data:
                return None, "Failed to create booking"
            
            supabase.table("slots") \
                .update({"is_booked": True}) \
                .eq("slot_id", slot["slot_id"]) \
                .execute()
            
            return {
                **response.data[0],
                "slot": slot
            }, None
        except Exception as e:
            return None, str(e)

    @staticmethod
    def get_user_bookings(user_id):
        try:
            response = supabase.table("bookings") \
                .select("""
                    *,
                    users!inner(
                        first_name,
                        last_name,
                        email
                    ),
                    slots!inner(
                        slot_id,
                        service_id,
                        start_time,
                        end_time,
                        is_booked
                    )
                """) \
                .eq("booked_by", user_id) \
                .order('booking_time', desc=True) \
                .execute()
            return response.data, None
        except Exception as e:
            return None, str(e)

    @staticmethod
    def get_booking_by_slot(slot_id):
        try:
            response = supabase.table("bookings") \
                .select("""
                    *,
                    users!inner(
                        first_name,
                        last_name,
                        email
                    ),
                    slots!inner(
                        slot_id,
                        service_id,
                        start_time,
                        end_time,
                        is_booked
                    )
                """) \
                .eq("slot_id", slot_id) \
                .single() \
                .execute()
            return response.data, None
        except Exception as e:
            return None, str(e)
