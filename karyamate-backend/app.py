from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///karyamate.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'super-secret-key'

db = SQLAlchemy(app)
jwt = JWTManager(app)
CORS(app)

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    passwordhash = db.Column(db.String(128), nullable=False)
    createdat = db.Column(db.DateTime, default=datetime.utcnow)
    tasks = db.relationship('Task', backref='user', lazy=True)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(255))
    completed = db.Column(db.Boolean, default=False)
    userid = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    createdat = db.Column(db.DateTime, default=datetime.utcnow)
    updatedat = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Authentication Endpoints
@app.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({"msg": "Email and password required"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "Email already exists"}), 400
    user = User(email=email, passwordhash=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()
    return jsonify({"id": user.id, "email": user.email}), 201

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.passwordhash, password):
        return jsonify({"msg": "Bad email or password"}), 401
    access_token = create_access_token(identity=user.id)
    return jsonify({"access_token": access_token, "token_type": "Bearer"}), 200

# Task CRUD Endpoints
@app.route('/tasks', methods=['GET'])
@jwt_required()
def get_tasks():
    user_id = get_jwt_identity()
    tasks = Task.query.filter_by(userid=user_id).all()
    return jsonify([{
        "id": t.id,
        "title": t.title,
        "description": t.description,
        "completed": t.completed
    } for t in tasks]), 200

@app.route('/tasks', methods=['POST'])
@jwt_required()
def create_task():
    user_id = get_jwt_identity()
    data = request.get_json()
    title = data.get('title')
    description = data.get('description', '')
    if not title:
        return jsonify({"msg": "Title is required"}), 400
    task = Task(title=title, description=description, userid=user_id)
    db.session.add(task)
    db.session.commit()
    return jsonify({
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "completed": task.completed
    }), 201

@app.route('/tasks/<int:task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    user_id = get_jwt_identity()
    task = Task.query.filter_by(id=task_id, userid=user_id).first()
    if not task:
        return jsonify({"msg": "Task not found"}), 404
    return jsonify({
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "completed": task.completed
    }), 200

@app.route('/tasks/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    user_id = get_jwt_identity()
    task = Task.query.filter_by(id=task_id, userid=user_id).first()
    if not task:
        return jsonify({"msg": "Task not found"}), 404
    data = request.get_json()
    title = data.get('title')
    description = data.get('description', '')
    completed = data.get('completed', False)
    if not title:
        return jsonify({"msg": "Title is required"}), 400
    task.title = title
    task.description = description
    task.completed = completed
    db.session.commit()
    return jsonify({
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "completed": task.completed
    }), 200

@app.route('/tasks/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    user_id = get_jwt_identity()
    task = Task.query.filter_by(id=task_id, userid=user_id).first()
    if not task:
        return jsonify({"msg": "Task not found"}), 404
    db.session.delete(task)
    db.session.commit()
    return jsonify({}), 204

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
