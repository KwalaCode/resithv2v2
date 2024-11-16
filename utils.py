from datetime import datetime, timedelta
from app.models import Booking, User
from app import db

def get_available_slots(day, is_team):
    booked_slots = Booking.query.filter_by(day=day).all()
    all_slots = ['08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00']
    if day.weekday() == 4:  # Friday
        all_slots = all_slots[:8]
    
    available_slots = [slot for slot in all_slots if slot not in [b.time_slot for b in booked_slots]]
    return available_slots

def can_book_this_week():
    return True  # Always allow booking for testing

def get_next_week_dates():
    now = datetime.now()
    days_ahead = 7 - now.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    next_monday = now + timedelta(days=days_ahead)
    return [next_monday + timedelta(days=i) for i in range(5)]  # Monday to Friday

def get_available_opponents(is_team):
    if is_team:
        return User.query.filter_by(is_team=True).all()
    else:
        return User.query.filter_by(is_team=False).all()

def has_booking_this_week(user_email):
    next_week_dates = get_next_week_dates()
    booking = Booking.query.filter(
        Booking.email1 == user_email,
        Booking.day.in_(next_week_dates)
    ).first()
    return booking is not None