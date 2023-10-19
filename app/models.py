from .config import db
from datetime import datetime
from enum import Enum
import pytz
from werkzeug.security import generate_password_hash

tz = pytz.timezone('Asia/Tehran')


class CustomerState(Enum):
    Introduction = "Introduction"
    Presentation = "Presentation"
    Negotiation = "Negotiation"
    Contract = "Contract"
    Deploy = "Deploy"
    Test = "Test"
    Report = "Report"
    Termination = "Termination"
    Active = "Active"


class Customer(db.Model):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(80), required=True)
    logo = db.Column(db.string(80), required=False)
    phone_number = db.Column(db.Integer, required=True)
    address = db.Column(db.String(100), required=True)
    state = db.Column(db.Enum(CustomerState), required=True)
    documents = db.relationship('Document', backref='customer', lazy=True)
    logs = db.relationship('Log', backref='customer', lazy=True)

    @classmethod    
    def find_by_company_name(cls, company_name):
        return cls.query.filter_by(company_name).first()


class Document(db.Model):
    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), required=True)
    filename = db.Column(db.String(100), required=True)


# This class is for logging the StateChange for a customer
class Log(db.Model):
    __tablename__ = 'logs'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), required=True)
    state = db.Column(db.Enum(CustomerState), required=True)
    timestamp = db.Column(db.DateTime, required=True, default= datetime.now(tz))


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(80))
    password = db.Column(db.String(80))

    def __init__(self, username, password):
        self.username = username
        self.password = generate_password_hash(password)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()
    
    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).first()
