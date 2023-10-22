from datetime import datetime
from enum import Enum
from werkzeug.security import generate_password_hash
from api.utils.db import db
from api.utils.CONST import (ALLOWED_EXTENSIONS_PHOTOS, 
                             ALLOWED_EXTENSIONS_DOCUMENTS, 
                             preferred_tz)


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
    company_name = db.Column(db.String(80))
    logo = db.Column(db.String(80))
    phone_number = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(100), nullable=False)
    state = db.Column(db.Enum(CustomerState), nullable=False)   
    documents = db.relationship('Document', backref='customers', lazy=True, cascade='all, delete-orphan')
    logs = db.relationship('Log', backref='customers', lazy=True, cascade='all, delete-orphan')

    def json(self):
        return {
            'id': self.id,
            'company_name': self.company_name,
            'logo': self.logo,
            'phone_number': self.phone_number,
            'address': self.address,
            'state': self.state.value,
            'documents': [document.filename for document in self.documents],
            'logs': [log.json() for log in self.logs]
        }
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        self.documents.clear()
        self.logs.clear()
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def allowed_logo_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_PHOTOS
    
    @staticmethod
    def is_valid_state(state):
        return state.lower() in [state.value.lower() for state in CustomerState]

    @classmethod    
    def find_by_company_name(cls, company_name):
        return cls.query.filter_by(company_name=company_name).first()
    
    @classmethod    
    def find_by_company_id(cls, company_id):
        return cls.query.filter_by(id=company_id).first()


class Document(db.Model):
    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'),  nullable=False)
    name = db.Column(db.String(80), nullable=False)
    filename = db.Column(db.String(100),  nullable=False)

    def json(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'name': self.name,
            'filename': self.filename
        }
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    
    @staticmethod
    def allowed_document_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_DOCUMENTS


# This class is for logging the StateChange for a customer
class Log(db.Model):
    __tablename__ = 'logs'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'),  nullable=False)
    state = db.Column(db.Enum(CustomerState),  nullable=False)
    timestamp = db.Column(db.DateTime,  nullable=False, default= datetime.now(preferred_tz))

    def json(self):
        return {
            'customer_id': self.customer_id,
            'state': self.state.value,
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(80))
    password = db.Column(db.String(80))

    def __init__(self, username, password):
        self.username = username
        self.password = generate_password_hash(password)

    def json(self):
        return {
            'id': self.id,
            'username': self.username, 
            }

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()
    
    @classmethod
    def find_by_id(cls, id):
        return cls.query.filter_by(id=id).first()






