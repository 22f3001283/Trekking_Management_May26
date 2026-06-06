from flask import Flask, jsonify, make_response, request
from datetime import datetime, timedelta
from flask_restful import Resource, Api
# from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS, cross_origin
from models import User, init_db, db
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
        def wrapper(*args, **kwargs):
            user = get_current_user()
            if user is None or user.role not in required_roles:
                return jsonify({"message": "Unauthorized access"}), 403
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
            response = jsonify({"msg": "User does not exist"})
            return make_response(response, 404)
        
        if not check_password_hash(user.password_hash, password):
            response = jsonify({"msg": "Incorrect password"})
            return make_response(response, 401)
        
        if not user.status:
            response = jsonify({"msg": "Wait till you are Verified"})
            return make_response(response, 409)

        access_token = create_access_token(identity=user.username)
        response = jsonify({"msg": "successfully logged in", "token": access_token, "username": user.username, "role": user.role})
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
        status = False
        rating = None
        created_at = datetime.now()
        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            response = jsonify({'msg': 'Username or Email already exists'})
            return make_response(response, 409)
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password_hash=hashed_password, role=role, contact=contact, status=status, rating=rating, created_at=created_at)
        db.session.add(new_user)
        db.session.commit()
        response = jsonify({"username": username, "email": email, "msg": "user created correctly"})
        return make_response(response, 200)

# ######################################################################################################################################################## #

# User Approval (Admin only)
class UserApprovalResource(Resource):
    @jwt_required()
    @role_required(["admin"])
    def get(self):
        users = User.query.filter_by(status=False).all()
        return jsonify([user.serialize() for user in users])

    @jwt_required()
    @role_required(["admin"])
    def put(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return jsonify({"msg": "User not found"})
        
        user.status = True
        db.session.commit()
        return jsonify({"msg": "User approved successfully"})

    @jwt_required()
    @role_required(["admin"])
    def delete(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return jsonify({"msg": "User not found"})
        
        db.session.delete(user)
        db.session.commit()
        return jsonify({"msg": "User rejected and removed"})


api.add_resource(Hello,'/')
api.add_resource(LoginResource,'/login')
api.add_resource(SignupResource,'/signup')
api.add_resource(UserApprovalResource,'/users/pending', '/users/<int:user_id>/approve', '/users/<int:user_id>/reject')

if __name__=="__main__":
    app.run(debug=True)
