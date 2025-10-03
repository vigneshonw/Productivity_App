from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date, timedelta
import random

app = Flask(__name__)
app.secret_key = 'replace_with_your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///productivity.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    sleep_hours = db.Column(db.Float, default=0.0)
    dopamine_level = db.Column(db.Float, default=0.0)  # Example metric

class MicroGoal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    description = db.Column(db.String(250), nullable=False)
    date_set = db.Column(db.Date, nullable=False)
    is_completed = db.Column(db.Boolean, default=False)

class ChallengeProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    day_number = db.Column(db.Integer, nullable=False)
    percentage = db.Column(db.Float, nullable=False)
    date_recorded = db.Column(db.Date, nullable=False)

# Routes
@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Username already exists.')
            return redirect(url_for('signup'))
        user = User(username=username, password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        flash('User created. Please login.')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))
        flash('Invalid credentials.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out.')
    return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET','POST'])
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    today = date.today()

    if request.method == 'POST':
        desc = request.form['goal_description']
        if desc.strip():
            goal = MicroGoal(user_id=user.id, description=desc, date_set=today)
            db.session.add(goal)
            db.session.commit()
            flash('Micro goal added.')

    goals = MicroGoal.query.filter_by(user_id=user.id, date_set=today).all()
    completed_goals = sum(1 for g in goals if g.is_completed)

    # Calculate today's streak
    streak = 0
    day_check = today
    while True:
        day_goals = MicroGoal.query.filter_by(user_id=user.id, date_set=day_check).all()
        if any(g.is_completed for g in day_goals):
            streak += 1
            day_check -= timedelta(days=1)
        else:
            break

    # Calculate streak for each of the last 7 days
    streak_counts = []
    for i in reversed(range(7)):
        streak_day = today - timedelta(days=i)
        streak_val = 0
        day_check = streak_day
        while True:
            day_goals = MicroGoal.query.filter_by(user_id=user.id, date_set=day_check).all()
            if any(g.is_completed for g in day_goals):
                streak_val += 1
                day_check -= timedelta(days=1)
            else:
                break
        streak_counts.append(streak_val)

    # Prepare last 7 days data for chart
    date_labels = []
    completion_counts = []
    for i in reversed(range(7)):  # last 7 days
        day = today - timedelta(days=i)
        day_goals = MicroGoal.query.filter_by(user_id=user.id, date_set=day).all()
        completed_count = sum(1 for g in day_goals if g.is_completed)
        date_labels.append(day.strftime("%a"))  # Day abbreviation, e.g. 'Mon'
        completion_counts.append(completed_count)

    quotes = [
        "The only way to do great work is to love what you do. – Steve Jobs",
        "Don’t watch the clock; do what it does. Keep going. – Sam Levenson",
        "Success is the sum of small efforts, repeated day in and day out. – Robert Collier",
        "It does not matter how slowly you go as long as you do not stop. – Confucius",
        "Your limitation—it’s only your imagination.",
        "Push yourself, because no one else is going to do it for you.",
        "Small daily improvements over time lead to stunning results.",
        "Great things never come from comfort zones.",
    ]
    quote = random.choice(quotes)

    return render_template('dashboard.html',
                           user=user,
                           goals=goals,
                           completed_goals=completed_goals,
                           streak=streak,
                           quote=quote,
                           date_labels=date_labels,
                           completion_counts=completion_counts,
                           streak_counts=streak_counts)

@app.route('/complete_goal/<int:goal_id>')
def complete_goal(goal_id):
    goal = MicroGoal.query.get(goal_id)
    if goal and goal.user_id == session.get('user_id'):
        goal.is_completed = True
        db.session.commit()
        flash('Goal marked as completed.')
    return redirect(url_for('dashboard'))

@app.route('/challenge', methods=['GET','POST'])
def challenge():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    today = date.today()

    progress = ChallengeProgress.query.filter_by(user_id=user_id).order_by(ChallengeProgress.day_number.desc()).first()
    next_day = 1 if not progress else progress.day_number + 1
    if next_day > 100:
        flash("Congratulations! You have completed the 100 days challenge!")
        next_day = 100

    if request.method == 'POST':
        cp = ChallengeProgress(user_id=user_id, day_number=next_day, percentage=next_day, date_recorded=today)
        db.session.add(cp)
        db.session.commit()
        flash(f"Day {next_day} completed! Keep improving!")
        next_day += 1
        if next_day > 100:
            next_day = 100

    completed_days = ChallengeProgress.query.filter_by(user_id=user_id).count()
    percentage = (completed_days / 100) * 100

    return render_template('challenge.html', day=next_day, completed=completed_days, percentage=percentage)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()   # Create tables at app startup inside app context
    app.run(debug=True)
