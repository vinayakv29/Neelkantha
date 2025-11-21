from . import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    
    # --- NEELKANTHA STATS ---
    # We use gaming terms internally, but show them as "Spiritual Stats" in UI
    pet_xp = db.Column(db.Integer, default=0)       # Karma Points
    pet_level = db.Column(db.Integer, default=1)    # Consciousness Level
    pet_health = db.Column(db.Integer, default=100) # Prana (Energy)
    
    entries = db.relationship('MoodEntry', backref='author', lazy=True)

class MoodEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mood_score = db.Column(db.Integer, nullable=False)
    note = db.Column(db.String(200), nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
