from crypt import methods
from datetime import datetime
from distutils.log import debug
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import json
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity,
    create_refresh_token
)
from datetime import timedelta

USERENAME = "aya"
PASSWORD = "00000"


DATABASE_URI = 'sqlite:///users.db'
# DATABASE_URI = 'postgres://postgres:1941997@localhost:5432/ToDo_DB'
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
app.config['JWT_SECRET_KEY'] = "mySecretKey"
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=4)

jwt = JWTManager(app)


@app.route('/login', methods=['POST'])
def login():
    data = json.loads(request.data)
    username = data['username']
    password = data['password']

    if username == USERENAME and password == PASSWORD:
        access_token = create_access_token(identity=username)
        return jsonify({
            'status': 'Success',
            'data': {
                'access_token': access_token,
            }
        })
    return jsonify({
            'status': 'Fail',
            'msg': "username or password is incorrect"
        })



@app.route('/protectedLogin', methods=['GET'])
@jwt_required()
def protected():
    username = get_jwt_identity()
    return jsonify({
            'status': 'success',
            'msg': f"welcome {username} to To do list"
        })


db = SQLAlchemy(app)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    details = db.Column(db.String)

    def __repr__(self):
        return f'Task("{self.name}", "{self.details}")'


@app.route('/task', methods=['GET', 'POST'])
def task():
    if request.method == "GET":
        tasks = Task.query.all()

        list_tasks = []
        for task in tasks:
            task_dict = {}
            task_dict["id"] = task.id
            task_dict["name"] = task.name
            task_dict["details"] = task.details
            list_tasks.append(task_dict)

        return jsonify({
            'tasks': list_tasks
        })

    elif request.method == "POST":
        id = request.json.get("id")
        name = request.json.get("name")
        details = request.json.get("details")

        # data = json.loads(request.data)
        # id = data['id']
        # name = data['name']
        # details = data['details']

        task = Task(id=id, name=name, details=details)
        # import ipdb; ipdb.set_tracr()
        # print(task)
        db.session.add(task)
        db.session.commit()

        return jsonify({
            "status": "success",
            "data": f"{name} task added successfully!"
        }), 201


@app.route('/task/<int:id>', methods=['PUT', 'GET', 'DELETE'])
def update_task(id):
    task = Task.query.filter_by(id=id).first()
    if request.method == 'GET':
        task_dict = {}
        task_dict["id"] = task.id
        task_dict["name"] = task.name
        task_dict["details"] = task.details

        return jsonify({
            'tasks': task_dict
        })

    if request.method == 'PUT':
        task.name = request.json.get('name')
        task.details = request.json.get('details')

        db.session.commit()
        return jsonify({
            "status": "success",
            "data": "task updated successfully!"
        })

    
    if request.method == 'DELETE':
        db.session.delete(task)
        db.session.commit()
        return jsonify({
            "status": "success",
            "data": "task deleted successfully!"
        })

@app.route("/")
def home():
    return "Hello, Flask!"


db.create_all()
app.run(debug=True, port=5005)