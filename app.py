import os
from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from api.resources.user import (UserResource, UserRegisterResource, 
                                  UserListResource, UserLoginResource)
from api.resources.customer import CustomerResource, CustomerListResource
from api.resources.document import (DocumentUploadResource, 
                                      DocumentDownloadResource,
                                      DocumentDeleteResource, 
                                      DocumentListResource, )
from api.resources.log import LogResource
from api.utils.db import db


baseDir = os.path.abspath(os.path.dirname(__file__))


app = Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@postgres:5432/databasename'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(baseDir, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'secretkey'
app.config['UPLOAD_FOLDER'] = "C:\\Users\\Asus\\Documents\\GitHub\\Customer_Management_API_Flask_RESTful\\uploads"
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
api.add_resource(DocumentUploadResource, '/customer/<int:customer_id>/upload-doc/<string:name>')
api.add_resource(DocumentDownloadResource, '/customer/<int:customer_id>/download-doc/<int:document_id>')
api.add_resource(DocumentDeleteResource, '/customer/<int:customer_id>/delete-doc/<int:document_id>')
api.add_resource(DocumentListResource, '/customer/<int:customer_id>/docs')
api.add_resource(LogResource, '/customer/<int:customer_id>/statelogs')
api.add_resource(UserRegisterResource, '/register')
api.add_resource(UserLoginResource, '/login')
api.add_resource(UserResource, '/user/<int:user_id>')
api.add_resource(UserListResource, '/users')



if __name__ == '__main__':
    app.run(debug=True)