from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_team = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_blocked = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_in_teams_database(self):
        return self.is_team

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email1 = db.Column(db.String(120), db.ForeignKey('user.email'), nullable=False)
    email2 = db.Column(db.String(120), nullable=False)
    time_slot = db.Column(db.String(20), nullable=False)
    day = db.Column(db.Date, nullable=False)
    is_team_booking = db.Column(db.Boolean, default=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_admin_user(email, password):
    admin_user = User.query.filter_by(email=email).first()
    if admin_user:
        admin_user.is_admin = True
    else:
        admin_user = User(email=email, is_admin=True)
        admin_user.set_password(password)
    db.session.add(admin_user)
    db.session.commit()
