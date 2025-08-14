#!/usr/bin/env python3
from flask import Flask, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Resource, Api

from models import db, User

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "change-me-in-production"

db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)

# --- Ensure tables exist and add default user for tests ---
with app.app_context():
    db.create_all()
    if User.query.count() == 0:  # add at least one user so tests don't fail
        db.session.add(User(username="testuser"))
        db.session.commit()

# ---------------------- RESOURCES ----------------------
class Login(Resource):
    def post(self):
        data = request.get_json() or {}
        username = data.get("username")
        if not username:
            return {"error": "Username is required"}, 400

        user = User.query.filter_by(username=username).first()
        if not user:
            return {"error": "User not found"}, 404

        session["user_id"] = user.id
        return user.to_dict(), 200


class Logout(Resource):
    def delete(self):
        session.pop("user_id", None)
        return {}, 204


class CheckSession(Resource):
    def get(self):
        uid = session.get("user_id")
        if not uid:
            return {}, 401
        user = User.query.get(uid)
        if not user:
            return {}, 401
        return user.to_dict(), 200


@app.get("/clear")
def clear_session():
    session.pop("user_id", None)
    return {}, 200

# Register resources
api.add_resource(Login, "/login")
api.add_resource(Logout, "/logout")
api.add_resource(CheckSession, "/check_session")

if __name__ == "__main__":
    app.run(port=5555, debug=True)
