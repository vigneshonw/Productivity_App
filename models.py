from database import db
from datetime import date

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)
    sleep_hours = db.Column(db.Float, default=0.0)
    dopamine_level = db.Column(db.Float, default=0.0)  # Example metric
    
    micro_goals = db.relationship('MicroGoal', back_populates='user', cascade="all, delete-orphan")
    challenge_progress = db.relationship('ChallengeProgress', back_populates='user', cascade="all, delete-orphan")

class MicroGoal(db.Model):
    __tablename__ = 'micro_goals'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    description = db.Column(db.String(250), nullable=False)
    date_set = db.Column(db.Date, nullable=False, default=date.today)
    is_completed = db.Column(db.Boolean, default=False)

    user = db.relationship('User', back_populates='micro_goals')

class ChallengeProgress(db.Model):
    __tablename__ = 'challenge_progress'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    day_number = db.Column(db.Integer, nullable=False)
    percentage = db.Column(db.Float, nullable=False)
    date_recorded = db.Column(db.Date, nullable=False, default=date.today)
    
    user = db.relationship('User', back_populates='challenge_progress')
