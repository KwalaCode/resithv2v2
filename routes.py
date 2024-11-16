from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User, Booking
from app.forms import LoginForm, SignupForm, BookingForm, AdminForm
from app import db
from app.utils import get_available_slots, can_book_this_week, get_next_week_dates, get_available_opponents, has_booking_this_week
from datetime import datetime
from functools import wraps
from functools import wraps
from flask import abort
from flask_login import current_user


main = Blueprint('main', __name__)
auth = Blueprint('auth', __name__)
booking = Blueprint('booking', __name__)
admin = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@main.route('/')
def index():
    next_week_dates = get_next_week_dates()
    bookings = Booking.query.filter(Booking.day.in_(next_week_dates)).all()
    return render_template('index.html', bookings=bookings)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password')
    return render_template('login.html', form=form)

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        user = User(email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully')
        return redirect(url_for('auth.login'))
    return render_template('signup.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@booking.route('/booking', methods=['GET', 'POST'])
@login_required
def make_booking():
    if current_user.is_blocked:
        flash('Your account is blocked from making reservations.')
        return redirect(url_for('main.index'))

    if has_booking_this_week(current_user.email):
        flash('You already have a booking for this week')
        return redirect(url_for('main.index'))

    form = BookingForm()
    form.opponent.choices = [(u.email, u.email) for u in get_available_opponents(current_user.is_in_teams_database())]
    
    if form.validate_on_submit():
        booking = Booking(
            email1=current_user.email,
            email2=form.opponent.data,
            time_slot=form.time_slot.data,
            day=datetime.strptime(request.form['day'], '%Y-%m-%d').date(),
            is_team_booking=current_user.is_in_teams_database()
        )
        db.session.add(booking)
        db.session.commit()
        flash('Booking successful')
        if not available_days:
            flash('No available days for booking.')
            return redirect(url_for('main.index'))
        return redirect(url_for('main.index'))
    next_week_dates = get_next_week_dates()
    available_days = next_week_dates[:3] if current_user.is_in_teams_database() else next_week_dates[3:]
    
    return render_template('booking.html', form=form, available_days=available_days)

@booking.route('/get_available_slots')
@login_required
def get_available_slots_route():
    day = request.args.get('day')
    if day:
        day = datetime.strptime(day, '%Y-%m-%d').date()
        slots = get_available_slots(day, current_user.is_in_teams_database())
        return jsonify(slots)
    return jsonify([])

@admin.route('/admin', methods=['GET', 'POST'])
@login_required
@admin_required
def admin_panel():
    form = AdminForm()
    users = User.query.all()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if form.action.data == 'add':
            if user:
                user.is_team = True
            else:
                new_user = User(email=form.email.data, is_team=True)
                db.session.add(new_user)
            flash('User added to Teams database')
        elif form.action.data == 'remove':
            if user:
                user.is_team = False
                flash('User removed from Teams database')
            else:
                flash('User not found')
        db.session.commit()
        return redirect(url_for('admin.admin_panel'))

    return render_template('admin.html', form=form, users=users)

@admin.route('/toggle_team_status', methods=['POST'])
@login_required
@admin_required
def toggle_team_status():
    data = request.json
    user_id = data.get('user_id')
    user = User.query.get(user_id)
    if user:
        user.is_team = not user.is_team
        db.session.commit()
        return jsonify({'success': True, 'is_team': user.is_team})
    return jsonify({'success': False}), 404

@admin.route('/toggle_blocked_status', methods=['POST'])
@login_required
@admin_required
def toggle_blocked_status():
    data = request.json
    user_id = data.get('user_id')
    user = User.query.get(user_id)
    if user:
        user.is_blocked = not user.is_blocked
        db.session.commit()
        return jsonify({'success': True, 'is_blocked': user.is_blocked})
    return jsonify({'success': False}), 404