from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_uploads import UploadSet, IMAGES, DOCUMENTS, configure_uploads


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@postgres:5432/databasename'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'secretkey'
app.config['UPLOADED_PHOTOS_DEST'] = 'uploads/photos'
app.config['UPLOADED_DOCUMENTS_DEST'] = 'uploads/documents'

db = SQLAlchemy(app)

api = Api(app)

jwt = JWTManager(app)

photos = UploadSet('photos', IMAGES)
documents = UploadSet('documents', DOCUMENTS)
configure_uploads(app, (photos, documents))

from app import models, resources

db.create_all()