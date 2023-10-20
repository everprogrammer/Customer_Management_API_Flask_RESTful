import os
from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
from files.resources import CustomerResource, CustomerListResource
from flask_migrate import Migrate

from db import db

baseDir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@postgres:5432/databasename'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(baseDir, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'secretkey'
app.secret_key = 'Amir'

db.init_app(app)

migrate = Migrate(app, db)

api = Api(app)

@app.before_first_request
def create_tables():
    db.create_all()

jwt = JWTManager(app)

api.add_resource(CustomerResource, '/customer/<string:company_name>')
api.add_resource(CustomerListResource, '/customers')


if __name__ == '__main__':
    app.run(debug=True)