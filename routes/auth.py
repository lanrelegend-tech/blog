from flask import Blueprint, request
from models import User
from extensions import db, bcrypt
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity
)
auth_bp = Blueprint("auth", __name__)



@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return {"error": "Username, email, and password are required"}, 400
    
    existing_username = User.query.filter_by(username=username).first()

    if existing_username:
        return {"error": "Username already exists"}, 409
    
    existing_email = User.query.filter_by(email=email).first()

    if existing_email:
         return {"error": "Email already exists"}, 409
    
    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

    new_user = User(
    username=username,
    email=email,
    password=hashed_password
          )


    db.session.add(new_user)
    db.session.commit()

    return {
    "message": "User registered successfully"
           }, 201




@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return {"error": "Email and password are required"}, 400

    user = User.query.filter_by(email=email).first()

    if not user:
        return {"error": "Invalid email or password"}, 401

    if not bcrypt.check_password_hash(user.password, password):
        return {"error": "Invalid email or password"}, 401

    access_token = create_access_token(identity=str(user.id))

    refresh_token = create_refresh_token(identity=str(user.id))

    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }, 200




@auth_bp.route("/profile", methods=["GET"])
@jwt_required()
def profile():
    user_id = get_jwt_identity()

    user = User.query.get(user_id)

    if not user:
        return {"error": "User not found"}, 404

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role
    }, 200