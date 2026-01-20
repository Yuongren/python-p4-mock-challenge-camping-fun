#!/usr/bin/env python3

from flask import Flask, request, jsonify, make_response
from flask_migrate import Migrate
from models import db, Activity, Camper, Signup
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}"
)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

db.init_app(app)
migrate = Migrate(app, db)


@app.route('/')
def home():
    return ''


# ---------------- CAMPERS ----------------

@app.get('/campers')
def get_campers():
    campers = Camper.query.all()
    return jsonify([
        camper.to_dict(only=('id', 'name', 'age'))
        for camper in campers
    ]), 200


@app.get('/campers/<int:id>')
def get_camper(id):
    camper = Camper.query.get(id)
    if not camper:
        return {"error": "Camper not found"}, 404
    return camper.to_dict(), 200


@app.post('/campers')
def create_camper():
    data = request.json
    try:
        camper = Camper(
            name=data.get('name'),
            age=data.get('age')
        )
        db.session.add(camper)
        db.session.commit()
        return camper.to_dict(only=('id', 'name', 'age')), 201
    except Exception:
        db.session.rollback()
        return {"errors": ["validation errors"]}, 400


@app.patch('/campers/<int:id>')
def update_camper(id):
    camper = Camper.query.get(id)
    if not camper:
        return {"error": "Camper not found"}, 404

    data = request.json
    try:
        camper.name = data.get('name', camper.name)
        camper.age = data.get('age', camper.age)
        db.session.commit()
        return camper.to_dict(only=('id', 'name', 'age')), 202
    except Exception:
        db.session.rollback()
        return {"errors": ["validation errors"]}, 400


# ---------------- ACTIVITIES ----------------

@app.get('/activities')
def get_activities():
    activities = Activity.query.all()
    return jsonify([
        activity.to_dict(only=('id', 'name', 'difficulty'))
        for activity in activities
    ]), 200


@app.delete('/activities/<int:id>')
def delete_activity(id):
    activity = Activity.query.get(id)
    if not activity:
        return {"error": "Activity not found"}, 404

    db.session.delete(activity)
    db.session.commit()
    return '', 204


# ---------------- SIGNUPS ----------------

@app.post('/signups')
def create_signup():
    data = request.json
    try:
        signup = Signup(
            time=data.get('time'),
            camper_id=data.get('camper_id'),
            activity_id=data.get('activity_id')
        )
        db.session.add(signup)
        db.session.commit()
        return signup.to_dict(), 201
    except Exception:
        db.session.rollback()
        return {"errors": ["validation errors"]}, 400


if __name__ == '__main__':
    app.run(port=5555, debug=True)
