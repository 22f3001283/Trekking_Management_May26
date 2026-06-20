from flask import Flask, jsonify, make_response, request
from datetime import datetime, timedelta
from flask_restful import Resource, Api
# from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS, cross_origin
from models import User, init_db, db, Trek, TrekStatus, UserRole, Booking, Participant, BookingStatus, PaymentStatus
import functools

app=Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type, Authorization'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
app.config["JWT_SECRET_KEY"] = "aStrongSecretKey"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)

api = Api(app)
jwt = JWTManager(app)
init_db(app)

CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

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
            response = jsonify({"msg": "Wait till you are Verified"})
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
        status = "inactive"
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
        response = jsonify({"username": username, "email": email, "msg": "user created correctly"})
        return make_response(response, 200)

# ######################################################################################################################################################## #

# Create-->post; Read-->get; Update-->put; Delete-->delete

# -------------------------------------------------------Trek--------------------------------------------------------------------------------------
class TrekListResource(Resource):
    @jwt_required()
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
        else:
            new_trek.status = requested_status

        db.session.add(new_trek)
        db.session.commit()

        if "images" in data and data["images"]:
            new_trek.images = data["images"]
            db.session.commit()

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

        if requested_status is not None:
            if requested_status in [TrekStatus.OPEN, TrekStatus.APPROVED]:
                if trek_is_complete(trek):
                    trek.status = requested_status
                else:
                    trek.status = TrekStatus.PENDING
                    msg = "Some fields are missing, so this trek was saved as Pending. Fill in all fields to mark it Open/Approved."
            else:
                trek.status = requested_status

            if requested_status == TrekStatus.COMPLETED:
                bookings = Booking.query.filter_by(trek_id=trek_id).filter(Booking.status == BookingStatus.BOOKED).all()
                for booking in bookings:
                    booking.status = BookingStatus.COMPLETED

        db.session.commit()
        return {"msg": msg, "trek": trek.serialize()}

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
        return {"msg": msg, "trek": trek.serialize()}

class UserBookingSummaryResource(Resource):
    @jwt_required()
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
 
        if trek.status not in [TrekStatus.OPEN, TrekStatus.APPROVED]:
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
        booking.payment_status=PaymentStatus.REFUND
        db.session.commit()
        return {"msg": "Booking cancelled successfully"}, 200
    
#-------------------------------------------------Pending Users------------------------------------------------------------------------------------
# User Approval (Admin only)
class UserApprovalResource(Resource):
    @jwt_required()
    @role_required(["admin"])
    def get(self):
        users = User.query.filter(User.status.in_(["inactive", "blacklisted"])).all()
        return jsonify([user.serialize() for user in users])

    @jwt_required()
    @role_required(["admin"])
    def put(self, user_id):
        user = User.query.get(user_id)
        data = request.get_json()
        status = data.get('status')
        if not user:
            return jsonify({"msg": "User not found"})
        
        user.status = status
        db.session.commit()
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
    def get(self):
        users = User.query.all()
        return jsonify([user.serialize() for user in users])

# - USER: only Open/Approved treks
class UserTrekListResource(Resource) :
    @jwt_required()
    def get(self):
        treks = Trek.query. filter(Trek.status.in_([TrekStatus. OPEN, TrekStatus.APPROVED]) ).all()
        return [trek.serialize() for trek in treks]

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

if __name__=="__main__":
    app.run(debug=True)
