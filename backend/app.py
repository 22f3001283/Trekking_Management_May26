from flask import Flask, jsonify, make_response, request
from datetime import datetime, timedelta
from flask_restful import Resource, Api
# from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS, cross_origin
from models import User, init_db, db, Trek, TrekStatus, UserRole
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
                return {"message": "Unauthorized access"}, 403
            return func(*args, **kwargs)
        return wrapper
    return decorator

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
        rating = None
        created_at = datetime.now()          
        if User.query.filter_by(email=email).first():
            response = jsonify({'msg': 'Email already exists, Please login'})
            return make_response(response, 409)
        elif User.query.filter_by(username=username).first():
            response = jsonify({'msg': 'Username already exists!'})
            return make_response(response, 409)  
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password_hash=hashed_password, role=role, contact=contact, status=status, rating=rating, created_at=created_at)
        db.session.add(new_user)
        db.session.commit()
        response = jsonify({"username": username, "email": email, "msg": "user created correctly"})
        return make_response(response, 200)

# ######################################################################################################################################################## #

# Create-->post; Read-->get; Update-->put; Delete-->delete

# Trek 
class TrekListResource(Resource):
    @jwt_required()
    def get(self):
        treks = Trek.query.all()
        return [trek.serialize() for trek in treks]

    @jwt_required()
    @role_required([UserRole.ADMIN])
    def post(self):
        print("=== POST /treks called ===")
        data = request.get_json() or {}
        print("Content-Type:", request.content_type)  # ← add this
        print("Received data:", {k: v for k, v in data.items() if k != 'images'})
        print("Data keys:", list(data.keys()))
        required_fields = ["trek_name", "location", "difficulty", "duration_days", "available_slots", "price", "start_date", "end_date", "assigned_staff_id"]
        missing = [field for field in required_fields if field not in data]
        print(missing)
        if missing:
            return {"msg": f"Missing required field(s): {', '.join(missing)}"}, 400

        new_trek = Trek(
            trek_name=data["trek_name"],
            location=data["location"],
            difficulty=data["difficulty"],
            duration_days=int(data["duration_days"]),
            available_slots=int(data["available_slots"]),
            price=float(data["price"]),
            start_date=datetime.strptime(data["start_date"], "%Y-%m-%d").date(),
            end_date=datetime.strptime(data["end_date"], "%Y-%m-%d").date(),
            status=data.get("status", TrekStatus.OPEN),
            assigned_staff_id=int(data.get("assigned_staff_id")) if data.get("assigned_staff_id") else None
        )
        print(new_trek)
        db.session.add(new_trek)
        db.session.commit()  # commit first to get trek_id

        # Save images
        if "images" in data and data["images"]:
            new_trek.images = data["images"]  # list of base64 strings
            db.session.commit()
        return {"msg": "Trek created successfully", "trek": new_trek.serialize()}, 201

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
        for field in ["trek_name", "location", "difficulty", "duration_days", "available_slots", "price", "start_date", "end_date", "status", "assigned_staff_id"]:
            if field in data:
                if field in ["start_date", "end_date"]:
                    setattr(trek, field, datetime.strptime(data[field], "%Y-%m-%d").date())
                elif field in ["duration_days", "available_slots", "assigned_staff_id"]:  # ← add this
                    setattr(trek, field, int(data[field]) if data[field] else None)
                else:
                    setattr(trek, field, data[field])
        if "images" in data and data["images"]:
            trek.images = data["images"] 

        db.session.commit()
        return {"msg": "Trek updated successfully", "trek": trek.serialize()}

    @jwt_required()
    @role_required([UserRole.ADMIN])
    def delete(self, trek_id):
        trek = Trek.query.get(trek_id)
        if not trek:
            return {"msg": "Trek not found"}, 404
        db.session.delete(trek)
        db.session.commit()
        return {"msg": "Trek deleted successfully"}

class TrekStaffUpdateResource(Resource):
    @jwt_required()
    @role_required([UserRole.STAFF])
    def put(self, trek_id):
        trek = Trek.query.get(trek_id)
        if not trek:
            return {"msg": "Trek not found"}, 404

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

        if "status" in data:
            if data["status"] not in [TrekStatus.OPEN, TrekStatus.CLOSED]:
                return {"msg": "Staff may only set status to Open or Closed"}, 400
            trek.status = data["status"]
            updated = True

        if data.get("complete") is True:
            trek.status = TrekStatus.COMPLETED
            updated = True

        if not updated:
            return {"msg": "No valid staff-managed trek fields provided"}, 400

        db.session.commit()  
        return {"msg": "Trek updated by staff successfully", "trek": trek.serialize()}

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
api.add_resource(TrekStaffUpdateResource, '/treks/<int:trek_id>/staff')

if __name__=="__main__":
    app.run(debug=True)
