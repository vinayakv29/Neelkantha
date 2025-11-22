from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from textblob import TextBlob  # Import the AI Brain
from . import db
from .models import User, MoodEntry

main = Blueprint('main', __name__)

# --- AUTHENTICATION ROUTES ---
@main.route('/')
def index():
    return redirect(url_for('main.login'))

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('main.dashboard'))
        flash('Invalid credentials.')
    return render_template('login.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if User.query.filter_by(username=username).first():
            flash('Username taken.')
            return redirect(url_for('main.register'))
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('main.login'))
    return render_template('register.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

# --- SMART DASHBOARD LOGIC ---
@main.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    message = None
    
    if request.method == 'POST':
        # ACTION 1: HEALING (Pranayama Button)
        if 'heal_action' in request.form:
            current_user.pet_health = min(100, current_user.pet_health + 25)
            current_user.pet_xp += 5
            message = "You performed Pranayama. Your Prana has increased!"
            db.session.commit()
            
        # ACTION 2: LOGGING MOOD (The Smart Part)
        elif 'score' in request.form:
            score = int(request.form.get('score'))
            note = request.form.get('note') or "" # Handle empty notes safely
            
            # My AI logic starts here (Using TextBlob)
            # 1. Analyze the text (Polarity: -1 is Negative, +1 is Positive)
            blob = TextBlob(note)
            sentiment = blob.sentiment.polarity 
            
            xp_gain = 10
            health_change = 0
            
            # Checking if user is fake happy (High score but sad words)
            # Example: Score 10, Text "I hate this so much"
            if score > 7 and sentiment < -0.2:
                health_change = -5 # Penalty for masking feelings
                xp_gain = 2 # Low XP
                message = "⚠️ CONFLICT DETECTED: You rated 10/10, but your words carry negative energy. True balance requires honesty."
            
            # Checking for "Mixed Signals" (Low score but positive/hopeful text)
            # Example: Score 2, Text "I am actually feeling amazing!"
            elif score < 4 and sentiment > 0.3:
                health_change = 0 # Neutralize the damage (don't hurt health)
                xp_gain = 5
                message = "🤔 MIXED SIGNALS: Your words are full of light, but your score is low. We kept your Prana stable."

            # NORMAL LOGIC (No Conflict found)
            elif score >= 7:
                health_change = 5
                message = "Positive alignment detected. Your Prana grows."
            elif score < 4:
                health_change = -10
                xp_gain = 15 # Reward for facing the truth
                message = "Processing negativity. The system acknowledges your pain."
            else:
                message = "Entry logged. Maintain your path."
            # --- AI ANALYSIS END ---

            # --- APPLY CHANGES TO DB ---
            current_user.pet_xp += xp_gain
            current_user.pet_health = min(100, max(0, current_user.pet_health + health_change))
            
            # Evolution Check
            if current_user.pet_xp >= current_user.pet_level * 50:
                current_user.pet_level += 1
                current_user.pet_xp = 0 
                current_user.pet_health = 100
                message = f"ASCENSION! Your consciousness reached Level {current_user.pet_level}!"
            
            # Finally saving the mood to the database
            new_entry = MoodEntry(mood_score=score, note=note, author=current_user)
            db.session.add(new_entry)
            db.session.commit()

    return render_template('dashboard.html', user=current_user, message=message)
