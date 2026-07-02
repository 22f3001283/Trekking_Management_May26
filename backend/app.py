from collections import defaultdict
import csv
from flask import send_from_directory   
from celery.result import AsyncResult
from flask import Flask, jsonify, make_response, request
from datetime import date, datetime, timedelta
from flask_restful import Resource, Api
# from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS, cross_origin
from models import User, init_db, db, Trek, TrekStatus, UserRole, UserStatus, Booking, Participant, BookingStatus, PaymentStatus
import functools
import os
from flask import Flask, request
from flask_restful import Api, Resource
from flask_mail import Mail, Message
from flask_caching import Cache
from celery import Celery
from dotenv import load_dotenv
from celery.schedules import crontab
from calendar import monthrange
from sqlalchemy import extract, func

# Load .env
load_dotenv()

app=Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type, Authorization'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
app.config["JWT_SECRET_KEY"] = "aStrongSecretKey"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)

api = Api(app)
jwt = JWTManager(app)
init_db(app)

CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# ============================
# Flask-Mail Configuration
# ============================
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USER')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASS')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USER')
mail = Mail(app)

# ============================
# Flask-Caching with Redis
# ============================
app.config['CACHE_TYPE'] = 'RedisCache'
app.config['CACHE_REDIS_HOST'] = 'localhost'
app.config['CACHE_REDIS_PORT'] = 6379
app.config['CACHE_REDIS_DB'] = 1
app.config['CACHE_REDIS_URL'] = 'redis://localhost:6379/1'
app.config['CACHE_DEFAULT_TIMEOUT'] = 60
cache = Cache(app)

# ============================
# Celery Configuration
# ============================
app.config['broker_url'] = os.getenv('BROKER_URL', 'redis://localhost:6379/0')
app.config['result_backend'] = os.getenv('RESULT_BACKEND', 'redis://localhost:6379/0')

celery = Celery(app.name, broker=app.config['broker_url'], backend=app.config['result_backend'])
celery.conf.broker_connection_retry_on_startup = True

# ============================
# Celery Context Setup
# ============================
def init_celery(flask_app):
    celery_app = Celery(
        flask_app.import_name,
        broker=flask_app.config['broker_url'],
        backend=flask_app.config['result_backend']
    )
    celery_app.conf.update(flask_app.config)

    class ContextTask(celery_app.Task):
        def __call__(self, *args, **kwargs):
            with flask_app.app_context():
                return super().__call__(*args, **kwargs)

    celery_app.Task = ContextTask
    return celery_app

celery = init_celery(app)

#---------------------------------------------------Export Path--------------------------------------------------------------------------------
EXPORT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "exports")
os.makedirs(EXPORT_DIR, exist_ok=True)
###################################  decorator  ############################################################################# #

def get_current_user():
    username = get_jwt_identity()
    return User.query.filter_by(username=username).first()

def role_required(required_roles):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            user = get_current_user()
            if user is None or user.role not in required_roles:
                return {"msg": "Unauthorized access"}, 403
            return func(*args, **kwargs)
        return wrapper
    return decorator

def trek_is_complete(trek):
    required_values = [
        trek.location, trek.difficulty, trek.available_slots,
        trek.price, trek.start_date, trek.end_date, trek.assigned_staff_id
    ]
    return all(v is not None for v in required_values)

##################################  API ROUTES  ###############################################

@app.route('/api',methods=['POST'])
def hello_world():
    return "Hello world!"

@app.route('/admin', methods=['GET','POST'])
def admin():
    return "Welcome to Admin Dashboard"

@app.route('/debug/me', methods=['GET'])
@jwt_required()
def debug_me():
    user = get_current_user()
    if not user:
        return {"msg": "No user found"}, 401
    return {"username": user.username, "role": user.role, "status": user.status}

@app.route('/user', methods=['GET','POST'])
def user():
    return "Welcome to User Dashboard"

##################################  Resources   ##################################################

class Hello(Resource):
    # @cross_origin()
    # @jwt_required()
    def get(self):
        # user_name=get_jwt_identity()
        return  {"msg" : "hello world"}
    
##################################  Authentication ###############################################

class LoginResource(Resource):
    def post(self):
        data = request.get_json()
        email = data['email']
        password = data[ 'password']
        user = User.query.filter_by(email=email).first()
        if not user:
            response = jsonify({"msg": "Email not registered. Sign up to begin your trekking journey!"})
            return make_response(response, 404)
        
        if not check_password_hash(user.password_hash, password):
            response = jsonify({"msg": "Incorrect password"})
            return make_response(response, 401)
        
        if user.status != "active":
            response = jsonify({"msg": "You have been blacklisted, please contact the support team."})
            return make_response(response, 409)

        access_token = create_access_token(identity=user.username)
        response = jsonify({"msg": "successfully logged in", "token": access_token, "username": user.username, "role": user.role, "user_id": user.user_id}) 
        return make_response(response, 200)

class SignupResource(Resource):
    @cross_origin()
    def post(self):
        data = request.get_json()
        username = data['username']
        email = data['email']
        password = data['password']
        role = "user"
        contact = data.get('contact', None)
        status = "active"
        created_at = datetime.now()          
        if User.query.filter_by(email=email).first():
            response = jsonify({'msg': 'Email already exists, Please login'})
            return make_response(response, 409)
        elif User.query.filter_by(username=username).first():
            response = jsonify({'msg': 'Username already exists!'})
            return make_response(response, 409)  
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password_hash=hashed_password, role=role, contact=contact, status=status, created_at=created_at)
        db.session.add(new_user)
        db.session.commit()
        cache.delete("users_all")
        cache.delete("admin_stats")
        response = jsonify({"username": username, "email": email, "msg": "user created correctly"})
        return make_response(response, 200)

# ######################################################################################################################################################## #

# Create-->post; Read-->get; Update-->put; Delete-->delete

# -------------------------------------------------------Trek--------------------------------------------------------------------------------------
class TrekListResource(Resource):
    @jwt_required()
    @cache.cached(timeout=120, key_prefix="treks_all")
    def get(self):
        treks = Trek.query.all()
        return [trek.serialize() for trek in treks]

    @jwt_required()
    @role_required([UserRole.ADMIN])
    def post(self):
        data = request.get_json() or {}
        if not data.get("trek_name"):
            return {"msg": "trek_name is required"}, 400

        new_trek = Trek(
            trek_name=data["trek_name"],
            location=data.get("location") or None,
            difficulty=data.get("difficulty") or None,
            duration_days=int(data["duration_days"]) if data.get("duration_days") not in (None, '', '0', 0) else None,
            available_slots=int(data["available_slots"]) if data.get("available_slots") not in (None, '') else None,
            price=float(data["price"]) if data.get("price") not in (None, '') else None,
            start_date=datetime.strptime(data["start_date"], "%Y-%m-%d").date() if data.get("start_date") else None,
            end_date=datetime.strptime(data["end_date"], "%Y-%m-%d").date() if data.get("end_date") else None,
            status=TrekStatus.PENDING,
            assigned_staff_id=int(data.get("assigned_staff_id")) if data.get("assigned_staff_id") not in (None, '') else None
        )

        requested_status = data.get("status", TrekStatus.PENDING)
        msg = "Trek created successfully"

        if requested_status == TrekStatus.CLOSED:
            new_trek.status = TrekStatus.PENDING
            msg = "A trek can't be Closed before it's been Open. Saved as Pending instead."
        elif requested_status in [TrekStatus.OPEN, TrekStatus.APPROVED]:
            if trek_is_complete(new_trek):
                new_trek.status = requested_status
            else:
                new_trek.status = TrekStatus.PENDING
                msg = "Some fields are missing, so this trek was saved as Pending. Fill in all fields to mark it Open/Approved."
        elif requested_status == TrekStatus.PENDING:
            new_trek.status = TrekStatus.PENDING
        else:
            return {"msg": f"Invalid status '{requested_status}'"}, 400

        db.session.add(new_trek)
        db.session.commit()

        if "images" in data and data["images"]:
            new_trek.images = data["images"]
            db.session.commit()

        cache.delete("treks_all")
        cache.delete("user_treks")
        cache.delete("admin_stats")

        return {"msg": msg, "trek": new_trek.serialize()}, 201    

class TrekResource(Resource):
    @jwt_required()
    def get(self, trek_id):
        trek = Trek.query.get(trek_id)
        if not trek:
            return {"msg": "Trek not found"}, 404
        return trek.serialize()

    @jwt_required()
    @role_required([UserRole.ADMIN])
    def put(self, trek_id):
        trek = Trek.query.get(trek_id)
        if not trek:
            return {"msg": "Trek not found"}, 404

        data = request.get_json() or {}
        old_status = trek.status
        requested_status = data.get("status")

        if requested_status == TrekStatus.CLOSED and old_status != TrekStatus.OPEN:
            return {"msg": "Trek must be Open before it can be Closed"}, 400

        for field in ["trek_name", "location", "difficulty", "duration_days", "available_slots", "price", "start_date", "end_date", "assigned_staff_id"]:
            if field in data:
                if field in ["start_date", "end_date"]:
                    setattr(trek, field, datetime.strptime(data[field], "%Y-%m-%d").date() if data[field] else None)
                elif field in ["duration_days", "available_slots", "assigned_staff_id"]:
                    setattr(trek, field, int(data[field]) if data[field] not in (None, '') else None)
                elif field in ["location", "difficulty"]:
                    setattr(trek, field, data[field] if data[field] not in (None, '') else None)
                else:
                    setattr(trek, field, data[field])

        if "images" in data and data["images"]:
            trek.images = data["images"]

        msg = "Trek updated successfully"
        cancelled_pending = []

        if requested_status is not None:
            if requested_status in [TrekStatus.OPEN, TrekStatus.APPROVED]:
                if trek_is_complete(trek):
                    trek.status = requested_status
                else:
                    trek.status = TrekStatus.PENDING
                    msg = "Some fields are missing, so this trek was saved as Pending. Fill in all fields to mark it Open/Approved."
            elif requested_status in [TrekStatus.CLOSED, TrekStatus.COMPLETED, TrekStatus.CANCELLED, TrekStatus.PENDING]:
                trek.status = requested_status
                if requested_status == TrekStatus.CLOSED:
                    cancelled_pending = cancel_pending_bookings_for_trek(trek)
                if requested_status == TrekStatus.COMPLETED:
                    bookings = Booking.query.filter_by(trek_id=trek_id).filter(Booking.status == BookingStatus.BOOKED).all()
                    for booking in bookings:
                        booking.status = BookingStatus.COMPLETED
            else:
                return {"msg": f"Invalid status '{requested_status}'"}, 400

        db.session.commit()

        for booking in cancelled_pending:
            send_pending_cancelled_email.delay(booking.booking_id)

        cache.delete("treks_all")
        cache.delete("user_treks")
        cache.delete("admin_stats")

        return {"msg": msg, "trek": trek.serialize()}

    @jwt_required()
    @role_required([UserRole.ADMIN])
    def delete(self, trek_id):
        trek = Trek.query.get(trek_id)
        if not trek:
            return {"msg": "Trek not found"}, 404

        existing_bookings = Booking.query.filter_by(trek_id=trek_id).first()
        if existing_bookings:
            return {"msg": "Cannot delete a trek that has bookings. Cancel or close it instead."}, 400

        db.session.delete(trek)
        db.session.commit()

        cache.delete("treks_all")
        cache.delete("user_treks")
        cache.delete("admin_stats")

        return {"msg": "Trek deleted successfully"}, 200
    
# ----------------------------------------------------------------Staff-------------------------------------------------------------------------

class StaffTrekListResource(Resource):
    """
    GET /staff/treks — returns only the treks assigned to the logged-in staff member
    """
    @jwt_required()
    @role_required([UserRole.STAFF])
    def get(self):
        current_user = get_current_user()
        treks = Trek.query.filter_by(assigned_staff_id=current_user.user_id).all()
        return [trek.serialize() for trek in treks]
    
class TrekStaffUpdateResource(Resource):
    @jwt_required()
    @role_required([UserRole.STAFF])
    def put(self, trek_id):
        trek = Trek.query.get(trek_id)
        if not trek:
            return {"msg": "Trek not found"}, 404
        
        current_user = get_current_user()
        if trek.assigned_staff_id != current_user.user_id:
            return {"msg": "Unauthorized - this trek is not assigned to you"}, 403
        
        data = request.get_json() or {}
        updated = False

        if "available_slots" in data:
            try:
                slots = int(data["available_slots"])
                if slots < 0:
                    return {"msg": "available_slots must be 0 or greater"}, 400
                trek.available_slots = slots
                updated = True
            except (TypeError, ValueError):
                return {"msg": "available_slots must be an integer"}, 400

        msg = "Trek updated by staff successfully"
        
        cancelled_pending = []
        if "status" in data:
            if data["status"] not in [TrekStatus.OPEN, TrekStatus.CLOSED]:
                return {"msg": "Staff may only set status to Open or Closed"}, 400

            if data["status"] == TrekStatus.CLOSED and trek.status != TrekStatus.OPEN:
                return {"msg": "Trek must be Open before it can be Closed"}, 400

            if data["status"] == TrekStatus.OPEN and not trek_is_complete(trek):
                trek.status = TrekStatus.PENDING
                msg = "Some fields are missing, so this trek was saved as Pending. Fill in all fields to mark it Open."
            else:
                trek.status = data["status"]
                if data["status"] == TrekStatus.CLOSED:
                    cancelled_pending = cancel_pending_bookings_for_trek(trek)
            updated = True

        if data.get("complete") is True:
            trek.status = TrekStatus.COMPLETED
            bookings = Booking.query.filter_by(trek_id=trek_id).filter(Booking.status == BookingStatus.BOOKED).all()
            for booking in bookings:
                booking.status = BookingStatus.COMPLETED
            updated = True

        if not updated:
            return {"msg": "No valid staff-managed trek fields provided"}, 400

        db.session.commit()

        for booking in cancelled_pending:
            send_pending_cancelled_email.delay(booking.booking_id)

        cache.delete("treks_all")
        cache.delete("user_treks")
        cache.delete("admin_stats")

        return {"msg": msg, "trek": trek.serialize()}

def _user_bookings_cache_key(*args, **kwargs):
    return f"user_bookings_{get_jwt_identity()}"

class UserBookingSummaryResource(Resource):
    @jwt_required()
    @cache.cached(timeout=30, make_cache_key=_user_bookings_cache_key)
    def get(self):
        current_user = get_current_user()
        bookings = Booking.query.filter_by(user_id=current_user.user_id).all()

        # latest booking per trek
        latest_map = {}
        for b in bookings:
            existing = latest_map.get(b.trek_id)
            if not existing or b.booking_date > existing.booking_date:
                latest_map[b.trek_id] = b

        result = []
        for b in latest_map.values():
            trek = Trek.query.get(b.trek_id)
            data = b.serialize()
            data['trek'] = trek.serialize() if trek else None
            result.append(data)

        return result, 200
    
#--------------------------------------------------------------------------Booking----------------------------------------------------------------

IST_OFFSET = timedelta(hours=5, minutes=30)   # Indian Standard Time
 
 
class BookingListResource(Resource):
    """
    POST /bookings  — create a new booking with participants (user)
    GET  /bookings  — list all bookings (admin / staff)
    """
 
    @jwt_required()
    def post(self):
        data = request.get_json() or {}
 
        trek_id        = data.get("trek_id")
        user_id        = data.get("user_id")
        payment_status = data.get("payment_status", PaymentStatus.PENDING)  # "Pending" | "Paid"
        participants   = data.get("participants", [])
 
        # ── validation ────────────────────────────────────────────────────
        if not trek_id or not user_id:
            return {"msg": "trek_id and user_id are required"}, 400
 
        if not participants:
            return {"msg": "At least one participant is required"}, 400
 
        trek = Trek.query.get(trek_id)
        if not trek:
            return {"msg": "Trek not found"}, 404
 
        if trek.status not in [TrekStatus.OPEN]:
            return {"msg": "Trek is not open for booking"}, 400
 
        if trek.available_slots < len(participants):
            return {"msg": f"Only {trek.available_slots} slot(s) available"}, 400
 
        existing_booking = Booking.query.filter_by(user_id=user_id, trek_id=trek_id).first()
        if existing_booking and existing_booking.status != BookingStatus.CANCELLED:
            return {"msg": "You have already booked this trek..."}, 409
 
        # ── create booking ────────────────────────────────────────────────
        # datetime is already imported at the top of app.py
        booking_date = datetime.utcnow() + IST_OFFSET   # store as IST naive datetime
 
        new_booking = Booking(
            user_id        = user_id,
            trek_id        = trek_id,
            booking_date   = booking_date,
            status         = BookingStatus.BOOKED,
            payment_status = payment_status,
        )
        db.session.add(new_booking)
        db.session.flush()   # get booking_id without committing yet
 
        # ── create participants ───────────────────────────────────────────
        for p in participants:
            name   = p.get("name", "").strip()
            dob    = p.get("dob")
            aadhar = p.get("aadhar", "").strip()
 
            if not name or not dob or not aadhar:
                db.session.rollback()
                return {"msg": "Each participant needs name, dob, and aadhar"}, 400
 
            if len(aadhar) != 12 or not aadhar.isdigit():
                db.session.rollback()
                return {"msg": f"Invalid Aadhar number for participant '{name}'"}, 400
 
            existing_participants = Participant.query.filter_by(aadhar=aadhar).all()

            for existing_p in existing_participants:
                existing_booking = Booking.query.get(existing_p.booking_id)
                if existing_booking and existing_booking.status != BookingStatus.CANCELLED:
                    existing_trek = Trek.query.get(existing_booking.trek_id)
                    if existing_trek and not (
                        existing_trek.end_date < trek.start_date or
                        existing_trek.start_date > trek.end_date
                    ):
                        db.session.rollback()
                        return {"msg": f"Participant with Aadhar {aadhar} already has an active booking on overlapping dates"}, 409
 
            db.session.add(Participant(
                booking_id = new_booking.booking_id,
                name       = name,
                dob        = datetime.strptime(dob, "%Y-%m-%d").date(),
                aadhar     = aadhar,
            ))
 
        # ── deduct slots & commit ─────────────────────────────────────────
        trek.available_slots -= len(participants)
 
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {"msg": "Booking failed — possible duplicate Aadhar or booking"}, 409

        cache.delete("treks_all")
        cache.delete("user_treks")
        cache.delete(f"user_bookings_{get_jwt_identity()}")
        cache.delete("admin_stats")

        return {
            "msg"          : "Booking successful",
            "booking"      : new_booking.serialize(),
            "participants" : [p.serialize() for p in new_booking.participants.all()]
        }, 201
 
    @jwt_required()
    def get(self):
        current_user = get_current_user()

        if current_user.role == UserRole.ADMIN:
            bookings = Booking.query.all()

        elif current_user.role == UserRole.STAFF:
            # Get only treks assigned to this staff member
            assigned_treks = Trek.query.filter_by(
                assigned_staff_id=current_user.user_id
            ).all()
            assigned_trek_ids = [t.trek_id for t in assigned_treks]
            bookings = Booking.query.filter(
                Booking.trek_id.in_(assigned_trek_ids)
            ).all()

        else:
            bookings = Booking.query.filter_by(user_id=current_user.user_id).all()

        return [b.serialize() for b in bookings], 200
 
 
class BookingResource(Resource):
    """
    GET    /bookings/<booking_id>  — fetch single booking + participants
    DELETE /bookings/<booking_id>  — cancel booking (user(who created) or admin)
    """
 
    @jwt_required()
    def get(self, booking_id):
        booking = Booking.query.get(booking_id)
        if not booking:
            return {"msg": "Booking not found"}, 404

        current_user = get_current_user()

        if current_user.role == UserRole.ADMIN:
            pass  # full access

        elif current_user.role == UserRole.STAFF:
            # Check if this booking's trek is assigned to this staff
            trek = Trek.query.get(booking.trek_id)
            if not trek or trek.assigned_staff_id != current_user.user_id:
                return {"msg": "Unauthorized"}, 403

        elif booking.user_id != current_user.user_id:
            return {"msg": "Unauthorized"}, 403

        return {
            "booking"      : booking.serialize(),
            "participants" : [p.serialize() for p in booking.participants.all()]
        }, 200
 
    @jwt_required()
    def delete(self, booking_id):
        booking = Booking.query.get(booking_id)
        if not booking:
            return {"msg": "Booking not found"}, 404

        current_user = get_current_user()
        if current_user.role != UserRole.ADMIN and booking.user_id != current_user.user_id:
            return {"msg": "Unauthorized"}, 403

        if booking.status == BookingStatus.CANCELLED:
            return {"msg": "Booking is already cancelled"}, 400   # ← guard added

        trek = Trek.query.get(booking.trek_id)
        if trek:
            trek.available_slots += booking.num_people

        booking.status = BookingStatus.CANCELLED
        if booking.payment_status == PaymentStatus.PAID:
            booking.payment_status = PaymentStatus.REFUND
        # else leave as Pendings
        db.session.commit()

        cache.delete("treks_all")
        cache.delete("user_treks")
        cache.delete(f"user_bookings_{get_jwt_identity()}")
        cache.delete("admin_stats")

        return {"msg": "Booking cancelled successfully"}, 200
    
#-------------------------------------------------Pending Users------------------------------------------------------------------------------------
# User Approval (Admin only)
class UserApprovalResource(Resource):
    @jwt_required()
    @role_required([UserRole.ADMIN])
    def get(self):
        users = User.query.filter(User.status.in_(["blacklisted"])).all()
        return jsonify([user.serialize() for user in users])

    @jwt_required()
    @role_required([UserRole.ADMIN])
    def put(self, user_id):
        user = User.query.get(user_id)
        data = request.get_json()
        status = data.get('status')
        if not user:
            return jsonify({"msg": "User not found"})
        
        user.status = status
        db.session.commit()
        cache.delete("users_all")
        cache.delete("admin_stats")
        send_status_change_notice.delay(user.user_id)
        return jsonify({"msg": "User status changed to "+status+" successfully"})

    # @jwt_required()
    # @role_required(["admin"])
    # def delete(self, user_id):
    #     user = User.query.get(user_id)
    #     if not user:
    #         return jsonify({"msg": "User not found"})
        
    #     db.session.delete(user)
    #     db.session.commit()
    #     return jsonify({"msg": "User rejected and removed"})

class UsersListResource(Resource):
    @jwt_required()
    @role_required([UserRole.ADMIN, UserRole.STAFF])
    @cache.cached(timeout=300, key_prefix="users_all")
    def get(self):
        users = User.query.all()
        return jsonify([user.serialize() for user in users])

# - USER: only Open/Approved treks
class UserTrekListResource(Resource) :
    @jwt_required()
    @cache.cached(timeout=120, key_prefix="user_treks")
    def get(self):
        treks = Trek.query. filter(Trek.status.in_([TrekStatus. OPEN, TrekStatus.APPROVED]) ).all()
        return [trek.serialize() for trek in treks]
    
# --------------------------------------------------------Admin Staff----------------------------------------------------------------------------

class StaffCreateResource(Resource):
    @jwt_required()
    @role_required([UserRole.ADMIN])
    def post(self):
        data = request.get_json() or {}
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        contact = data.get('contact')

        if not username or not email or not password:
            return {"msg": "username, email, and password are required"}, 400

        if User.query.filter_by(email=email).first():
            return {"msg": "Email already exists"}, 409
        if User.query.filter_by(username=username).first():
            return {"msg": "Username already exists"}, 409

        new_staff = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role=UserRole.STAFF,
            contact=contact,
            status="active",
            created_at=datetime.now()
        )
        db.session.add(new_staff)
        db.session.commit()
        cache.delete("users_all")
        cache.delete("admin_stats")
        return {"msg": "Staff member created successfully", "user": new_staff.serialize()}, 201


#-------------------------------------------------------------User Profile----------------------------------------------------------------------

class UserProfileResource(Resource):
    """
    GET /user/profile  — fetch the logged-in user's own profile
    PUT /user/profile  — update the logged-in user's own profile
    """
 
    @jwt_required()
    def get(self):
        current_user = get_current_user()
        if not current_user:
            return {"msg": "User not found"}, 404
        return current_user.serialize(), 200
 
    @jwt_required()
    def put(self):
        current_user = get_current_user()
        if not current_user:
            return {"msg": "User not found"}, 404
 
        data = request.get_json() or {}
 
        new_username = data.get("username")
        new_email = data.get("email")
 
        # Uniqueness checks only if the value is actually changing
        if new_username and new_username != current_user.username:
            if User.query.filter_by(username=new_username).first():
                return {"msg": "Username already exists"}, 409
            current_user.username = new_username
 
        if new_email and new_email != current_user.email:
            if User.query.filter_by(email=new_email).first():
                return {"msg": "Email already exists"}, 409
            current_user.email = new_email
 
        if "contact" in data:
            current_user.contact = data["contact"] or None
 
        # Optional password change — only if both fields are supplied
        new_password = data.get("new_password")
        if new_password:
            current_password = data.get("current_password")
            if not current_password or not check_password_hash(current_user.password_hash, current_password):
                return {"msg": "Current password is incorrect"}, 401
            current_user.password_hash = generate_password_hash(new_password)
 
        db.session.commit()
        return {"msg": "Profile updated successfully", "user": current_user.serialize()}, 200


#-----------------------------------------------------------------Admin Stats------------------------------------------------------------------
class AdminStatsResource(Resource):
    @jwt_required()
    @role_required([UserRole.ADMIN])
    @cache.cached(timeout=120, key_prefix="admin_stats")
    def get(self):
        # ---------- latest booking per (user, trek) ----------
        # booking_id is auto-increment, so MAX(booking_id) per (user_id, trek_id)
        # is always that pair's most recent booking (booked -> cancelled -> rebooked etc.)
        latest_booking_ids_sq = (
            db.session.query(func.max(Booking.booking_id).label("booking_id"))
            .group_by(Booking.user_id, Booking.trek_id)
            .subquery()
        )
        latest_only = Booking.booking_id.in_(
            db.session.query(latest_booking_ids_sq.c.booking_id)
        )

        # ---------- shared subquery: participant count per booking ----------
        participant_counts_sq = (
            db.session.query(
                Participant.booking_id.label("booking_id"),
                func.count(Participant.participant_id).label("cnt"),
            )
            .group_by(Participant.booking_id)
            .subquery()
        )

        # ---------- KPIs ----------
        total_treks = Trek.query.count()
        total_bookings = Booking.query.filter(latest_only).count()
        total_participants = (
            db.session.query(func.count(Participant.participant_id))
            .join(Booking, Booking.booking_id == Participant.booking_id)
            .filter(latest_only)
            .scalar()
        ) or 0
        total_users = User.query.filter_by(role=UserRole.USER).count()

        revenue_scalar = (
            db.session.query(func.sum(Trek.price * participant_counts_sq.c.cnt))
            .select_from(Booking)
            .join(Trek, Booking.trek_id == Trek.trek_id)
            .join(participant_counts_sq, participant_counts_sq.c.booking_id == Booking.booking_id)
            .filter(Booking.payment_status == PaymentStatus.PAID)
            .filter(latest_only)
            .scalar()
        )
        total_confirmed_revenue = round(revenue_scalar or 0, 2)

        cancelled_bookings = Booking.query.filter(
            Booking.status == BookingStatus.CANCELLED, latest_only
        ).count()
        cancellation_rate = round((cancelled_bookings / total_bookings * 100), 2) if total_bookings else 0

        # ---------- Most Popular Treks (top 8 by participant count) ----------
        popular_rows = (
            db.session.query(
                Trek.trek_name,
                func.count(Participant.participant_id).label("participant_count"),
            )
            .select_from(Trek)
            .join(Booking, Booking.trek_id == Trek.trek_id)
            .join(Participant, Participant.booking_id == Booking.booking_id)
            .filter(latest_only)
            .group_by(Trek.trek_id)
            .order_by(func.count(Participant.participant_id).desc())
            .limit(8)
            .all()
        )
        popular_treks = {
            "labels": [r.trek_name for r in popular_rows],
            "data": [r.participant_count for r in popular_rows],
        }

        # ---------- Booking Trends over time ----------
        booking_trend_rows = (
            db.session.query(
                func.strftime("%Y-%m", Booking.booking_date).label("month"),
                func.count(Booking.booking_id).label("cnt"),
            )
            .filter(latest_only)
            .group_by("month")
            .order_by("month")
            .all()
        )
        booking_trends = {
            "labels": [r.month for r in booking_trend_rows],
            "data": [r.cnt for r in booking_trend_rows],
        }

        # ---------- Monthly Participation ----------
        participation_rows = (
            db.session.query(
                func.strftime("%Y-%m", Booking.booking_date).label("month"),
                func.count(Participant.participant_id).label("cnt"),
            )
            .join(Participant, Participant.booking_id == Booking.booking_id)
            .filter(latest_only)
            .group_by("month")
            .order_by("month")
            .all()
        )
        monthly_participation = {
            "labels": [r.month for r in participation_rows],
            "data": [r.cnt for r in participation_rows],
        }

        # ---------- User Registrations per month (unaffected — not booking-derived) ----------
        user_reg_rows = (
            db.session.query(
                func.strftime("%Y-%m", User.created_at).label("month"),
                func.count(User.user_id).label("cnt"),
            )
            .group_by("month")
            .order_by("month")
            .all()
        )
        user_registrations = {
            "labels": [r.month for r in user_reg_rows],
            "data": [r.cnt for r in user_reg_rows],
        }

        # ---------- Treks by status (unaffected — not booking-derived) ----------
        status_month_rows = (
            db.session.query(
                func.strftime("%Y-%m", Trek.created_at).label("month"),
                Trek.status,
                func.count(Trek.trek_id).label("cnt"),
            )
            .group_by("month", Trek.status)
            .order_by("month")
            .all()
        )
        months = sorted({r.month for r in status_month_rows})
        all_statuses = [
            TrekStatus.PENDING, TrekStatus.APPROVED, TrekStatus.OPEN,
            TrekStatus.CLOSED, TrekStatus.COMPLETED, TrekStatus.CANCELLED,
        ]
        status_counts = {s: {m: 0 for m in months} for s in all_statuses}
        for r in status_month_rows:
            status_counts[r.status][r.month] = r.cnt

        treks_by_status = {
            "labels": months,
            "datasets": [
                {"label": status, "data": [status_counts[status][m] for m in months]}
                for status in all_statuses
            ],
        }

        # ---------- Booking Status breakdown ----------
        status_rows = (
            db.session.query(Booking.status, func.count(Booking.booking_id))
            .filter(latest_only)
            .group_by(Booking.status)
            .all()
        )
        booking_status_breakdown = {
            "labels": [r[0] for r in status_rows],
            "data": [r[1] for r in status_rows],
        }

        # ---------- Difficulty distribution (unaffected — not booking-derived) ----------
        diff_rows = (
            db.session.query(Trek.difficulty, func.count(Trek.trek_id))
            .group_by(Trek.difficulty)
            .all()
        )
        difficulty_distribution = {
            "labels": [r[0] or "Unspecified" for r in diff_rows],
            "data": [r[1] for r in diff_rows],
        }

        # ---------- Cancellation rate over time ----------
        total_per_month_rows = (
            db.session.query(
                func.strftime("%Y-%m", Booking.booking_date).label("month"),
                func.count(Booking.booking_id).label("total"),
            )
            .filter(latest_only)
            .group_by("month")
            .all()
        )
        cancelled_per_month_rows = (
            db.session.query(
                func.strftime("%Y-%m", Booking.booking_date).label("month"),
                func.count(Booking.booking_id).label("cancelled"),
            )
            .filter(Booking.status == BookingStatus.CANCELLED)
            .filter(latest_only)
            .group_by("month")
            .all()
        )
        total_map = {r.month: r.total for r in total_per_month_rows}
        cancelled_map = {r.month: r.cancelled for r in cancelled_per_month_rows}
        cancel_months = sorted(total_map.keys())
        cancellation_rate_trend = {
            "labels": cancel_months,
            "data": [
                round((cancelled_map.get(m, 0) / total_map[m] * 100), 2) if total_map[m] else 0
                for m in cancel_months
            ],
        }

        # ---------- Revenue trend (Paid only) ----------
        revenue_rows = (
            db.session.query(
                func.strftime("%Y-%m", Booking.booking_date).label("month"),
                func.sum(Trek.price * participant_counts_sq.c.cnt).label("revenue"),
            )
            .select_from(Booking)
            .join(Trek, Booking.trek_id == Trek.trek_id)
            .join(participant_counts_sq, participant_counts_sq.c.booking_id == Booking.booking_id)
            .filter(Booking.payment_status == PaymentStatus.PAID)
            .filter(latest_only)
            .group_by("month")
            .order_by("month")
            .all()
        )
        revenue_trend = {
            "labels": [r.month for r in revenue_rows],
            "data": [round(r.revenue or 0, 2) for r in revenue_rows],
        }

        return {
            "kpis": {
                "total_treks": total_treks,
                "total_bookings": total_bookings,
                "total_participants": total_participants,
                "total_users": total_users,
                "total_confirmed_revenue": total_confirmed_revenue,
                "cancellation_rate": cancellation_rate,
            },
            "charts": {
                "popular_treks": popular_treks,
                "booking_trends": booking_trends,
                "monthly_participation": monthly_participation,
                "user_registrations": user_registrations,
                "treks_by_status": treks_by_status,
                "booking_status_breakdown": booking_status_breakdown,
                "difficulty_distribution": difficulty_distribution,
                "cancellation_rate_trend": cancellation_rate_trend,
                "revenue_trend": revenue_trend,
            },
        }, 200
    
#-------------------------------------------Public Stats------------------------------------------------------------

class PublicStatsResource(Resource):
    """
    GET /public/stats — no auth required, safe for the homepage.
    Only exposes aggregate, non-identifying numbers.
    """
    @cache.cached(timeout=600, key_prefix="public_stats")
    def get(self):
        today = date.today()
        current_year = today.year

        # ---- de-dup: latest booking per (user, trek), same logic as admin stats ----
        latest_booking_ids_sq = (
            db.session.query(func.max(Booking.booking_id).label("booking_id"))
            .group_by(Booking.user_id, Booking.trek_id)
            .subquery()
        )
        latest_only = Booking.booking_id.in_(
            db.session.query(latest_booking_ids_sq.c.booking_id)
        )

        # ---- % of treks completed ----
        total_treks_ever = Trek.query.count()
        completed_treks = Trek.query.filter_by(status=TrekStatus.COMPLETED).count()
        completion_rate = round((completed_treks / total_treks_ever * 100), 1) if total_treks_ever else 0

        # ---- available / upcoming treks right now ----
        upcoming_treks = Trek.query.filter(
            Trek.status.in_([TrekStatus.OPEN, TrekStatus.APPROVED])
        ).count()

        # ---- unique participants (distinct aadhar, from active bookings only) ----
        unique_participants = (
            db.session.query(func.count(func.distinct(Participant.aadhar)))
            .join(Booking, Booking.booking_id == Participant.booking_id)
            .filter(Booking.status != BookingStatus.CANCELLED)
            .filter(latest_only)
            .scalar()
        ) or 0

        # ---- unique treks offered (by name) & unique destinations ----
        unique_trek_names = db.session.query(func.count(func.distinct(Trek.trek_name))).scalar() or 0
        unique_destinations = (
            db.session.query(func.count(func.distinct(Trek.location)))
            .filter(Trek.location.isnot(None))
            .scalar()
        ) or 0

        # ---- difficulty mix, currently open/approved only ----
        diff_rows = (
            db.session.query(Trek.difficulty, func.count(Trek.trek_id))
            .filter(Trek.status.in_([TrekStatus.OPEN, TrekStatus.APPROVED]))
            .filter(Trek.difficulty.isnot(None))
            .group_by(Trek.difficulty)
            .all()
        )
        difficulty_mix = {d: c for d, c in diff_rows}

        # ---- treks conducted: this year vs last year (by start_date, COMPLETED only) ----
        treks_this_year = Trek.query.filter(
            Trek.status == TrekStatus.COMPLETED,
            extract('year', Trek.start_date) == current_year,
        ).count()
        treks_last_year = Trek.query.filter(
            Trek.status == TrekStatus.COMPLETED,
            extract('year', Trek.start_date) == current_year - 1,
        ).count()

        # ---- busiest month (calendar month, across all years, COMPLETED treks) ----
        month_rows = (
            db.session.query(
                extract('month', Trek.start_date).label('m'),
                func.count(Trek.trek_id).label('cnt'),
            )
            .filter(Trek.status == TrekStatus.COMPLETED, Trek.start_date.isnot(None))
            .group_by('m')
            .order_by(func.count(Trek.trek_id).desc())
            .first()
        )
        month_names = ["", "January", "February", "March", "April", "May", "June",
                       "July", "August", "September", "October", "November", "December"]
        busiest_month = month_names[int(month_rows.m)] if month_rows else None

        # ---- average treks per month, last 12 months ----
        twelve_months_ago = today - timedelta(days=365)
        recent_trek_count = Trek.query.filter(
            Trek.status == TrekStatus.COMPLETED,
            Trek.start_date >= twelve_months_ago,
        ).count()
        avg_treks_per_month = round(recent_trek_count / 12, 1)

        # ---- total participant-days delivered (completed treks only) ----
        participant_days_scalar = (
            db.session.query(func.sum(Trek.duration_days * Booking.num_people if False else 1))
            .scalar()
        )
        # duration_days * participant count, summed across completed bookings on completed treks
        pd_rows = (
            db.session.query(Trek.duration_days, Booking.booking_id)
            .join(Booking, Booking.trek_id == Trek.trek_id)
            .filter(Trek.status == TrekStatus.COMPLETED, Booking.status == BookingStatus.COMPLETED)
            .filter(latest_only)
            .all()
        )
        participant_counts = dict(
            db.session.query(Participant.booking_id, func.count(Participant.participant_id))
            .group_by(Participant.booking_id).all()
        )
        total_participant_days = sum(
            (dur or 0) * participant_counts.get(bid, 0) for dur, bid in pd_rows
        )

        # ---- growth trends: participants & treks over time (monthly) ----
        participant_growth_rows = (
            db.session.query(
                func.strftime("%Y-%m", Booking.booking_date).label("month"),
                func.count(Participant.participant_id).label("cnt"),
            )
            .join(Participant, Participant.booking_id == Booking.booking_id)
            .filter(Booking.status != BookingStatus.CANCELLED)
            .filter(latest_only)
            .group_by("month")
            .order_by("month")
            .all()
        )
        trek_growth_rows = (
            db.session.query(
                func.strftime("%Y-%m", Trek.created_at).label("month"),
                func.count(Trek.trek_id).label("cnt"),
            )
            .group_by("month")
            .order_by("month")
            .all()
        )

        # ---- featured / most popular trek by name (active bookings only) ----
        featured_row = (
            db.session.query(Trek.trek_name, func.count(Participant.participant_id).label("cnt"))
            .join(Booking, Booking.trek_id == Trek.trek_id)
            .join(Participant, Participant.booking_id == Booking.booking_id)
            .filter(Booking.status != BookingStatus.CANCELLED)
            .filter(latest_only)
            .group_by(Trek.trek_id)
            .order_by(func.count(Participant.participant_id).desc())
            .first()
        )

        return {
            "completion_rate_pct": completion_rate,
            "upcoming_treks": upcoming_treks,
            "unique_participants": unique_participants,
            "unique_treks_offered": unique_trek_names,
            "unique_destinations": unique_destinations,
            "difficulty_mix": difficulty_mix,
            "treks_this_year": treks_this_year,
            "treks_last_year": treks_last_year,
            "busiest_month": busiest_month,
            "avg_treks_per_month": avg_treks_per_month,
            "total_participant_days": total_participant_days,
            "featured_trek": featured_row.trek_name if featured_row else None,
            "growth": {
                "participants": {
                    "labels": [r.month for r in participant_growth_rows],
                    "data": [r.cnt for r in participant_growth_rows],
                },
                "treks": {
                    "labels": [r.month for r in trek_growth_rows],
                    "data": [r.cnt for r in trek_growth_rows],
                },
            },
        }, 200

#-------------------------------------------Export Booking History------------------------------------------------------------------------------

class ExportBookingHistoryResource(Resource):
    @jwt_required()
    def post(self):
        current_user = get_current_user()
        task = export_booking_history_csv.delay(current_user.user_id)
        return {"task_id": task.id}, 202


class ExportStatusResource(Resource):
    @jwt_required()
    def get(self, task_id):
        result = AsyncResult(task_id, app=celery)
        if result.state == "SUCCESS":
            return {"status": "SUCCESS", "filename": result.result}, 200
        if result.state == "FAILURE":
            return {"status": "FAILURE"}, 500
        return {"status": result.state}, 200


class ExportDownloadResource(Resource):
    @jwt_required()
    def get(self, filename):
        current_user = get_current_user()

        if filename.startswith(f"booking_history_{current_user.user_id}_"):
            return send_from_directory(EXPORT_DIR, filename, as_attachment=True)

        if filename.startswith("participants_trek_"):
            try:
                trek_id = int(filename.split("_")[2])
            except (IndexError, ValueError):
                return {"msg": "Invalid filename"}, 400
            trek = Trek.query.get(trek_id)
            if not trek:
                return {"msg": "Trek not found"}, 404
            if current_user.role == UserRole.ADMIN or (
                current_user.role == UserRole.STAFF and trek.assigned_staff_id == current_user.user_id
            ):
                return send_from_directory(EXPORT_DIR, filename, as_attachment=True)
            return {"msg": "Unauthorized"}, 403

        return {"msg": "Unauthorized"}, 403
    

class ExportTrekParticipantsResource(Resource):
    @jwt_required()
    @role_required([UserRole.STAFF, UserRole.ADMIN])
    def post(self, trek_id):
        current_user = get_current_user()
        trek = Trek.query.get(trek_id)
        if not trek:
            return {"msg": "Trek not found"}, 404
        if current_user.role == UserRole.STAFF and trek.assigned_staff_id != current_user.user_id:
            return {"msg": "Unauthorized — this trek is not assigned to you"}, 403

        data = request.get_json() or {}
        include_cancelled = bool(data.get("include_cancelled", False))

        task = export_trek_participants_csv.delay(trek_id, include_cancelled)
        return {"task_id": task.id}, 202

api.add_resource(Hello,'/')
api.add_resource(LoginResource,'/login')
api.add_resource(SignupResource,'/signup')
api.add_resource(UsersListResource, '/users')
api.add_resource(UserTrekListResource, '/user/treks')
api.add_resource(UserApprovalResource,'/users/pending', '/users/<int:user_id>')
api.add_resource(TrekListResource, '/treks')
api.add_resource(TrekResource, '/treks/<int:trek_id>')
api.add_resource(StaffTrekListResource, '/staff/treks')
api.add_resource(TrekStaffUpdateResource, '/treks/<int:trek_id>/staff')
api.add_resource(UserBookingSummaryResource, '/user/bookings')
api.add_resource(BookingListResource, '/bookings')
api.add_resource(BookingResource, '/bookings/<int:booking_id>')
api.add_resource(StaffCreateResource, '/staff')
api.add_resource(UserProfileResource, '/user/profile')
api.add_resource(ExportBookingHistoryResource, '/export/booking-history')
api.add_resource(ExportStatusResource, '/export/status/<string:task_id>')
api.add_resource(ExportDownloadResource, '/export/download/<string:filename>')
api.add_resource(ExportTrekParticipantsResource, '/export/trek-participants/<int:trek_id>')
api.add_resource(AdminStatsResource, '/admin/stats')
api.add_resource(PublicStatsResource, '/public/stats')


#-----------------------------------------------------Scheduling Tasks------------------------------------------------------------------------------

@celery.task(name="tasks.send_daily_reminders")
def send_daily_reminders():
    with app.app_context():
        today = date.today()
        bookings = Booking.query.filter_by(status=BookingStatus.BOOKED).all()
        upcoming = [b for b in bookings if b.trek and b.trek.start_date and b.trek.start_date >= today]

        if not upcoming:
            print("[Daily Reminders] No upcoming booked treks.")
            return "No upcoming booked treks"

        by_user = defaultdict(list)
        for b in upcoming:
            by_user[b.user_id].append(b)

        sent = 0
        for user_id, user_bookings in by_user.items():
            user = user_bookings[0].user
            if not user or not user.email:
                continue

            trek_lines = "\n\n".join(
                f" {b.trek.trek_name} ({b.trek.location or 'TBD'})\n"
                f"  Start Date     :  {b.trek.start_date}\n"
                f"  End Date       :  {b.trek.end_date}\n"
                f"  Difficulty     :  {b.trek.difficulty or 'N/A'}\n"
                f"  Booking Status :  {b.status}\n"
                f"  Payment Status :  {b.payment_status}"
                for b in user_bookings
            )

            body = (
                f"Hi {user.username},\n\n"
                f"Here's a reminder of your upcoming trek(s):\n\n"
                f"{trek_lines}\n\n"
                f"If any Payment Status above shows Pending, please complete payment soon to keep your slot.\n\n"
                f"If you wish to cancel your booking, please ensure that the cancellation request is made before the registration period closes.\n\n"
                f"Kindly note that after the registration deadline has passed, cancellations will not be accepted and no refunds will be provided.\n\n"
                f"- TMA Team"
            )

            try:
                mail.send(Message(
                    subject="Reminder: Your upcoming trek(s) with TMA",
                    recipients=[user.email],
                    body=body,
                ))
                sent += 1
            except Exception as e:
                print(f"[Daily Reminders] Failed to email {user.email}: {e}")

        print(f"[Daily Reminders] Sent {sent} reminder email(s).")
        return f"Sent {sent} reminder email(s)."

@celery.task(name="tasks.send_close_warning_notice")
def send_close_warning_notice():
    with app.app_context():
        target_date = date.today() + timedelta(days=2)
        treks = Trek.query.filter(
            Trek.start_date == target_date,
            Trek.status != TrekStatus.CLOSED
        ).all()

        if not treks:
            print(f"[Close Warning] No open treks starting on {target_date}.")
            return "No treks to warn about"

        admin = User.query.filter_by(role=UserRole.ADMIN).first()
        sent = 0

        for trek in treks:
            recipients = set()
            if trek.assigned_staff and trek.assigned_staff.email:
                recipients.add(trek.assigned_staff.email)
            if admin and admin.email:
                recipients.add(admin.email)

            if not recipients:
                continue

            body = (
                f"Hi ,\n\n"
                f"The trek '{trek.trek_name}' starts on {trek.start_date} (2 days from now) "
                f"and is still '{trek.status}', not Closed.\n\n"
                f"Please close it manually before then. If it isn't closed, the system will "
                f"automatically close it at 7:05 AM the day before the trek starts, and any "
                f"bookings with pending payment will be cancelled at that time.\n\n"
                f"- TMA System"
            )
            try:
                mail.send(Message(
                    subject=f"Action needed: Please close '{trek.trek_name}' before it starts",
                    recipients=list(recipients),
                    body=body,
                ))
                sent += 1
            except Exception as e:
                print(f"[Close Warning] Failed to email for trek {trek.trek_id}: {e}")

        print(f"[Close Warning] {target_date}: {sent} warning email(s) sent.")
        return f"{sent} warning email(s) sent."
    
@celery.task(name="tasks.send_trek_notice")
def send_trek_notice():
    with app.app_context():
        target_date = date.today() + timedelta(days=1)
        treks = Trek.query.filter_by(start_date=target_date).all()

        if not treks:
            print(f"[Trek Notice] No treks starting on {target_date}.")
            return "No treks starting tomorrow"

        sent, auto_closed, cancelled_total = 0, 0, 0

        # only one admin exists in the system
        admin = User.query.filter_by(role=UserRole.ADMIN).first()

        for trek in treks:

            # Auto-close only if still Pending/Open/Approved
            if trek.status in [
                TrekStatus.PENDING,
                TrekStatus.APPROVED,
                TrekStatus.OPEN,
            ]:
                trek.status = TrekStatus.CLOSED
                auto_closed += 1

                cancelled_pending = cancel_pending_bookings_for_trek(trek)
                db.session.commit()

                cancelled_total += len(cancelled_pending)

                for booking in cancelled_pending:
                    send_pending_cancelled_email.delay(booking.booking_id)

                # Notify assigned staff + admin that system auto-closed trek
                recipients = set()

                if trek.assigned_staff and trek.assigned_staff.email:
                    recipients.add(trek.assigned_staff.email)

                if admin and admin.email:
                    recipients.add(admin.email)

                if recipients:
                    body = (
                        f"Hi,\n\n"
                        f"The trek '{trek.trek_name}' (starting {trek.start_date}) "
                        f"was not closed manually, so it has now been automatically CLOSED.\n\n"
                        f"{len(cancelled_pending)} booking(s) with pending payment "
                        f"were cancelled as a result.\n\n"
                        f"- TMA System"
                    )

                    try:
                        mail.send(Message(
                            subject=f"Auto-closed: '{trek.trek_name}'",
                            recipients=list(recipients),
                            body=body,
                        ))
                    except Exception as e:
                        print(f"[Trek Notice] Failed to send auto-close email: {e}")

            # Reminder to everyone still Booked
            bookings = Booking.query.filter_by(
                trek_id=trek.trek_id,
                status=BookingStatus.BOOKED
            ).all()

            for booking in bookings:
                user = booking.user
                if not user or not user.email:
                    continue

                participants = booking.participants.all()
                participant_lines = "\n".join(
                    f"  - {p.name}- Aadhar Number: {p.aadhar} (DOB: {p.dob})" for p in participants
                ) or "  - No participants found for this booking"

                body = (
                    f"Hi {user.username},\n\n"
                    f"Your trek '{trek.trek_name}' begins tomorrow — here are the details:\n\n"
                    f"  Trek       : {trek.trek_name}\n"
                    f"  Location   : {trek.location or 'TBD'}\n"
                    f"  Start Date : {trek.start_date}\n"
                    f"  End Date   : {trek.end_date}\n"
                    f"  Difficulty : {trek.difficulty or 'N/A'}\n\n"
                    f"Participants registered under this booking:\n"
                    f"{participant_lines}\n\n"
                    f"Before you head out, please keep these in mind:\n\n"
                    f"  1. Arrive at the meeting point sharp at 7:00 AM tomorrow.\n"
                    f"  2. Carry your Aadhar card with you — it's required for verification.\n"
                    f"  3. Pack according to the trek's difficulty and duration.\n"
                    f"  4. No refund will be issued for no-shows, so please plan accordingly.\n\n"
                    f"We're looking forward to having you on the trail!\n\n"
                    f"- TMA Team"
                )
                try:
                    mail.send(Message(
                        subject=f"Reminder: {trek.trek_name} starts tomorrow!",
                        recipients=[user.email],
                        body=body,
                    ))
                    sent += 1
                except Exception as e:
                    print(f"[Trek Notice] Failed to email {user.email}: {e}")
        print(
            f"[Trek Notice] {target_date}: "
            f"{sent} reminder(s), "
            f"{auto_closed} auto-closed, "
            f"{cancelled_total} cancelled."
        )

        return (
            f"{sent} reminder(s), "
            f"{auto_closed} auto-closed trek(s), "
            f"{cancelled_total} cancelled booking(s)."
        )
    

@celery.task(name="tasks.send_status_change_notice")
def send_status_change_notice(user_id):
    with app.app_context():
        user = User.query.get(user_id)
        if not user:
            return "User not found"
        
        if user.status == UserStatus.ACTIVE:
            body = f"""
Hello {user.username},

We are pleased to inform you that your account status has been updated to Active.

You can now access all the features and services available on our platform.

If you have any questions or need assistance, please feel free to contact our support team.

Thank you for being with us.

Best regards,

TMA Team
            """

        else:
            body = f"""
Hello {user.username},

This is to inform you that your account status has been updated to Blacklisted.

As a result, your access to certain features or services may be restricted.

If you believe this has been done in error or would like more information, please contact our support team.

Thank you for your understanding.

Best regards,

TMA Team
            """

        try:
            mail.send(Message(
                subject="Important Update Regarding Your Account",
                recipients=[user.email],   # recipients should be a list
                body=body,
            ))
            print(f"Status update email sent to user {user.user_id}")
            return "Email sent successfully."

        except Exception as e:
            print(f"Failed to email user {user.user_id}: {e}")
 
            return "Failed to send email."


@celery.task(name="tasks.export_booking_history_csv")
def export_booking_history_csv(user_id):
    with app.app_context():
        bookings = Booking.query.filter_by(user_id=user_id).all()

        filename = f"booking_history_{user_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.csv"
        filepath = os.path.join(EXPORT_DIR, filename)

        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Booking ID", "User ID", "Trek Name", "Location", "Booking Status", "Trek Start Date", "Trek End Date", "Booked on" , "No. of Participants"])
            for b in bookings:
                writer.writerow([
                    b.booking_id,
                    b.user_id,
                    b.trek.trek_name if b.trek else "",
                    b.trek.location if b.trek else "",
                    b.status,
                    b.trek.start_date,
                    b.trek.end_date,
                    b.booking_date.strftime("%Y-%m-%d %H:%M:%S") if b.booking_date else "",
                    b.num_people,
                ])

        return filename
    
@celery.task(name="tasks.export_trek_participants_csv")
def export_trek_participants_csv(trek_id, include_cancelled):
    with app.app_context():
        query = Booking.query.filter_by(trek_id=trek_id)
        if not include_cancelled:
            query = query.filter(Booking.status != BookingStatus.CANCELLED)
        bookings = query.all()

        filename = f"participants_trek_{trek_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.csv"
        filepath = os.path.join(EXPORT_DIR, filename)

        with open(filepath, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Participant Name", "DOB", "Aadhar", "Booked By", "Payment Status", "Booking Status"])
            for b in bookings:
                booked_by = b.user.username if b.user else ""
                for p in b.participants.all():
                    writer.writerow([
                        p.name,
                        p.dob.isoformat() if p.dob else "",
                        p.aadhar,
                        booked_by,
                        b.payment_status,
                        b.status,
                    ])

        return filename


@celery.task(name="tasks.send_pending_cancelled_email")
def send_pending_cancelled_email(booking_id):
    with app.app_context():
        booking = Booking.query.get(booking_id)
        if not booking:
            return "Booking not found"
        user, trek = booking.user, booking.trek
        if not user or not user.email:
            return "User not found or no email"

        body = (
            f"Hi {user.username},\n\n"
            f"Your booking for '{trek.trek_name}' has been automatically CANCELLED "
            f"because the trek has been closed and your payment was still pending.\n\n"
            f"Booking ID : {booking.booking_id}\n\n"
            f"You're welcome to book another available trek.\n\n- TMA Team"
        )
        try:
            mail.send(Message(subject=f"Booking cancelled: {trek.trek_name}",
                               recipients=[user.email], body=body))
            return f"Sent to {user.email}"
        except Exception as e:
            print(f"[Pending Cancel] Failed to email {user.email}: {e}")
            return f"Failed: {e}"

@celery.task(name="tasks.generate_monthly_report")
def generate_monthly_report():
    with app.app_context():
        today = date.today()
        if today.month == 1:
            report_month, report_year = 12, today.year - 1
        else:
            report_month, report_year = today.month, today.year

        month_name = date(report_year, report_month, 1).strftime("%B %Y")

        treks_conducted = Trek.query.filter(
            Trek.status == TrekStatus.COMPLETED,
            extract('month', Trek.start_date) == report_month,
            extract('year', Trek.start_date) == report_year,
        ).all()

        trek_ids = [t.trek_id for t in treks_conducted]
        bookings = []
        if trek_ids:
            bookings = Booking.query.filter(
                Booking.trek_id.in_(trek_ids),
                Booking.status.in_([BookingStatus.BOOKED, BookingStatus.COMPLETED])
            ).all()

        participant_user_ids = {b.user_id for b in bookings}

        # Total participants: sum of num_people across COMPLETED bookings only,
        # on treks that are COMPLETED and started in this month
        completed_bookings = [b for b in bookings if b.status == BookingStatus.COMPLETED]
        total_participants = sum(b.num_people or 0 for b in completed_bookings)

        booking_counts = {}
        for b in bookings:
            booking_counts[b.trek_id] = booking_counts.get(b.trek_id, 0) + 1
        top_trek_ids = sorted(booking_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        popular_treks = []
        for trek_id, count in top_trek_ids:
            trek = Trek.query.get(trek_id)
            if trek:
                popular_treks.append((trek.trek_name, count))

        html_body = _build_report_html(
            month_name,
            len(treks_conducted),
            len(participant_user_ids),
            total_participants,
            popular_treks,
        )

        admins = User.query.filter_by(role=UserRole.ADMIN).all()
        recipients = [a.email for a in admins if a.email]

        if not recipients:
            print("[Monthly Report] No admin email found.")
            return "No admin email found"

        try:
            mail.send(Message(
                subject=f"TMA Monthly Activity Report - {month_name}",
                recipients=recipients,
                html=html_body,
            ))
            print(f"[Monthly Report] Sent for {month_name} to {recipients}")
            return f"Report sent for {month_name}"
        except Exception as e:
            print(f"[Monthly Report] Failed to send: {e}")
            return f"Failed: {e}"

#-----------------------------------------------------------------------------------Backend Jobs------------------------------------------------------------------------------------

def cancel_pending_bookings_for_trek(trek):
    """Cancel Booked+Pending-payment bookings for a trek (e.g. when it closes).
    Frees slots immediately; returns affected bookings so emails can be sent after commit."""
    pending_bookings = Booking.query.filter_by(
        trek_id=trek.trek_id, status=BookingStatus.BOOKED, payment_status=PaymentStatus.PENDING
    ).all()

    for booking in pending_bookings:
        if trek.available_slots is not None:
            trek.available_slots += booking.num_people
        booking.status = BookingStatus.CANCELLED

    return pending_bookings

def _build_report_html(month_name, treks_count, users_count, total_participants, popular_treks):
    # Build ranked rows for popular treks with a visual bar + medal for top 3
    medals = ["🥇", "🥈", "🥉"]
    max_count = max((c for _, c in popular_treks), default=1)

    if popular_treks:
        rows = ""
        for i, (name, count) in enumerate(popular_treks):
            rank_label = medals[i] if i < 3 else f"#{i+1}"
            bar_width = max(int((count / max_count) * 100), 8)
            rows += f"""
            <tr>
              <td style="padding:14px 8px; font-size:20px; text-align:center; width:40px;">{rank_label}</td>
              <td style="padding:14px 8px;">
                <div style="font-weight:600; color:#1f2937; font-size:14px; margin-bottom:6px;">{name}</div>
                <div style="background:#eef2f7; border-radius:6px; height:8px; width:100%; overflow:hidden;">
                  <div style="background:linear-gradient(90deg,#6366f1,#8b5cf6); height:8px; width:{bar_width}%; border-radius:6px;"></div>
                </div>
              </td>
              <td style="padding:14px 8px; text-align:right; white-space:nowrap;">
                <span style="font-weight:700; color:#4f46e5; font-size:15px;">{count}</span>
                <span style="color:#9ca3af; font-size:12px;"> bookings</span>
              </td>
            </tr>
            """
    else:
        rows = """
        <tr>
          <td colspan="3" style="padding:24px 8px; text-align:center; color:#9ca3af; font-size:14px;">
            No bookings recorded this month
          </td>
        </tr>
        """

    return f"""
    <html>
      <body style="margin:0; padding:0; background:#f3f4f6; font-family:'Segoe UI', Arial, sans-serif;">
        <div style="max-width:600px; margin:0 auto; padding:24px 16px;">

          <!-- Header card -->
          <div style="background:linear-gradient(135deg,#4f46e5,#7c3aed); border-radius:16px 16px 0 0; padding:32px 28px; color:#ffffff;">
            <div style="font-size:13px; letter-spacing:1.5px; text-transform:uppercase; opacity:0.85; margin-bottom:6px;">
              TMA Monthly Activity Report
            </div>
            <div style="font-size:26px; font-weight:700;">{month_name}</div>
          </div>

          <!-- Stat cards -->
          <div style="background:#ffffff; padding:24px 20px;">
            <table width="100%" cellpadding="0" cellspacing="0">
              <tr>
                <td width="33.33%" style="padding-right:5px; vertical-align:top;">
                  <div style="background:#f5f3ff; border-radius:12px; padding:16px 10px; text-align:center;">
                    <div style="font-size:26px; font-weight:800; color:#6d28d9;">{treks_count}</div>
                    <div style="font-size:11px; color:#6b7280; margin-top:4px; text-transform:uppercase; letter-spacing:0.3px;">
                      Treks Conducted
                    </div>
                    <div style="font-size:9px; color:#9ca3af; margin-top:5px; line-height:1.4;">
                      Completed treks starting in {month_name}
                    </div>
                  </div>
                </td>
                <td width="33.33%" style="padding:0 5px; vertical-align:top;">
                  <div style="background:#eff6ff; border-radius:12px; padding:16px 10px; text-align:center;">
                    <div style="font-size:26px; font-weight:800; color:#2563eb;">{users_count}</div>
                    <div style="font-size:11px; color:#6b7280; margin-top:4px; text-transform:uppercase; letter-spacing:0.3px;">
                      Users Participated
                    </div>
                    <div style="font-size:9px; color:#9ca3af; margin-top:5px; line-height:1.4;">
                      Unique users on those completed treks
                    </div>
                  </div>
                </td>
                <td width="33.33%" style="padding-left:5px; vertical-align:top;">
                  <div style="background:#ecfdf5; border-radius:12px; padding:16px 10px; text-align:center;">
                    <div style="font-size:26px; font-weight:800; color:#059669;">{total_participants}</div>
                    <div style="font-size:11px; color:#6b7280; margin-top:4px; text-transform:uppercase; letter-spacing:0.3px;">
                      Total Participants
                    </div>
                    <div style="font-size:9px; color:#9ca3af; margin-top:5px; line-height:1.4;">
                      Headcount across completed bookings
                    </div>
                  </div>
                </td>
              </tr>
            </table>
          </div>

          <!-- Popular treks -->
          <div style="background:#ffffff; padding:4px 20px 24px;">
            <div style="font-size:15px; font-weight:700; color:#1f2937; margin-bottom:4px; padding-top:8px; border-top:1px solid #f0f0f0;">
              🏔️ Most Popular Treks
            </div>
            <table width="100%" cellpadding="0" cellspacing="0" style="margin-top:8px;">
              {rows}
            </table>
          </div>

          <!-- Footer -->
          <div style="background:#ffffff; border-radius:0 0 16px 16px; padding:18px 20px; text-align:center; border-top:1px solid #f0f0f0;">
            <div style="font-size:12px; color:#9ca3af;">
              Automated report generated by TMA System &middot; {month_name}
            </div>
          </div>

        </div>
      </body>
    </html>
    """


#-----------------------------------Celery---------------------------------------

celery.conf.timezone = 'Asia/Kolkata'
celery.conf.beat_schedule = {
    'daily_reminder': {
        'task': 'tasks.send_daily_reminders',
        'schedule': crontab(hour=7,minute=0),
    },
    'close_warning_notice': {
        'task': 'tasks.send_close_warning_notice',
        'schedule': crontab(hour=6,minute=45),
    },    
    'trek_notice':{
        'task': 'tasks.send_trek_notice',
        'schedule': crontab(hour=7,minute=5)
    },
    'monthly_report': {
        'task': 'tasks.generate_monthly_report',
        'schedule': crontab(day_of_month=1, hour=7, minute=15),
    },
}


if __name__=="__main__":
    app.run(debug=True)
