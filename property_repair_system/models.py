from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    userid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    userpassword = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)

class Repair(db.Model):
    __tablename__ = 'repairs'

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, nullable=False)
    repair_type = db.Column(db.String(50))
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.now)

class Assignment(db.Model):
    __tablename__ = 'assignments'

    id = db.Column(db.Integer, primary_key=True)
    repair_id = db.Column(db.Integer, nullable=False)
    worker_id = db.Column(db.Integer, nullable=False)
    assigned_at = db.Column(db.DateTime, default=datetime.now)

class MaintenanceRecord(db.Model):
    __tablename__ = 'maintenance_records'

    id = db.Column(db.Integer, primary_key=True)
    repair_id = db.Column(db.Integer, nullable=False)
    worker_id = db.Column(db.Integer, nullable=False)
    result = db.Column(db.Text)
    cost = db.Column(db.Numeric(10, 2))
    completed_at = db.Column(db.DateTime, default=datetime.now)

class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    repair_id = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Numeric(10, 2))
    status = db.Column(db.String(20), default='unpaid')
    paid_at = db.Column(db.DateTime)