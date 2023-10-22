from flask_restful import Resource, reqparse
from werkzeug.security import check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token

from api.models import User


class UserResource(Resource):
    @classmethod
    def get(cls, user_id):
        user = User.find_by_id(user_id)
        if not user:
            return {'message': 'User not found!'}, 404
        return user.json()
    
    @classmethod
    def delete(cls, user_id):
        user = User.find_by_id(user_id)
        if not user:
            return {'message': 'User not found!'}, 404
        user.delete_from_db()
        return {'message': 'User deleted successfullys.'}, 200
    

class UserListResource(Resource):
    def get(self):
        return [user.json() for user in User.query.all()]


class UserRegisterResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('username', type=str, required=True)
    parser.add_argument('password', type=str, required=True)

    def post(self):
        data = UserRegisterResource.parser.parse_args()

        if User.find_by_username(data['username']):
            return {'message': 'Username has already been taken!'}
        user = User(**data)
        user.save_to_db()

        return {'message': f"User ({data['username']}) has been created successfully!"}


class UserLoginResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('username', type=str, required=True)
    parser.add_argument('password', type=str, required=True)

    @classmethod
    def post(cls):
        data = cls.parser.parse_args()

        user = User.find_by_username(data['username'])

        if user and check_password_hash(user.password, data['password']):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(identity=user.id)
            return {
                'access_token': str(access_token),
                'refresh_token': str(refresh_token)
            }, 200
        
        return {'message': 'Invalid credentials'}, 401

