import os
from flask_restful import Resource, reqparse
from flask import request, make_response
from flask import send_from_directory
# from .models import Customer, Document, Log, User
from werkzeug.utils import secure_filename
from datetime import datetime
from api.utils.CONST import preferred_tz
from flask_jwt_extended import jwt_required

from api.models import Customer, Document, Log



class CustomerResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('phone_number', type=int, required=True)
    parser.add_argument('address', type=str, required=True)
    parser.add_argument('state', type=str, required=True)

    @jwt_required()
    def post(self, company_name):
        upload_folder = "C:\\Users\\Asus\\Documents\\GitHub\\Customer_Management_API_Flask_RESTful\\uploads"

        customer = Customer.find_by_company_name(company_name)
        if customer:
            return {'message': f"Company ({company_name}) already exists!"}, 400

        if not Customer.is_valid_state(request.form['state']):
            return {'message': 'Invalid state provided, please provide a valid state'}, 403
        
        # # # LOGO UPLOADS
        if 'logo' in request.files:
            logo = request.files['logo']
            if logo:
                if not Customer.allowed_logo_file(logo.filename):
                    return {'message': 'Invalid file type for logo. Allowed types: jpg, jpeg, png'}, 400
                filename = secure_filename(logo.filename)
                logo.save(os.path.join(upload_folder, filename))
        else:
            filename=None


        new_customer = Customer(
            company_name= company_name,
            logo=filename,
            phone_number=request.form['phone_number'],
            address=request.form['address'],
            state=request.form['state']
        )


        try:
            new_customer.save_to_db()
        except Exception as e:
            return {'message': f'An error occurred inserting the customer!error{str(e)}'}, 500 
        
        new_log = Log(
            customer_id = new_customer.id,
            state = request.form['state'],
            timestamp = datetime.now(preferred_tz)
                    )

        try:
            new_log.save_to_db()
        except Exception as e:
            return {'message': f'An error occurred inserting the log!error{str(e)}'}, 500 

        return new_customer.json(), 201
      

    def get(self, company_name):
        customer = Customer.find_by_company_name(company_name)

        if customer:
            return customer.json(), 200
        return {'message': f'Customer ({company_name}) was not found!'}, 404
    
    @jwt_required()
    def delete(self, company_name):
        customer = Customer.find_by_company_name(company_name)

        if customer:
            customer.delete_from_db()
        return {'message': 'Customer deleted successfully'}, 200
    
    @jwt_required()
    def put(self, company_name):
        customer = Customer.find_by_company_name(company_name)

        upload_folder = "C:\\Users\\Asus\\Documents\\GitHub\\Customer_Management_API_Flask_RESTful\\uploads"

        if not customer:
            return {'message': f'Customer ({company_name}) was not found!'}, 404

        if not Customer.is_valid_state(request.form['state']):
            return {'message': 'Invalid state provided, please provide a valid state'}, 400
        
        filename = customer.logo
        if 'logo' in request.files:
            logo = request.files['logo']
            if logo:
                if not Customer.allowed_logo_file(logo.filename):
                    return {'message': 'Invalid file type for logo. Allowed types: jpg, jpeg, png'}, 400
                filename = secure_filename(logo.filename)
                logo.save(os.path.join(upload_folder, filename))


        if customer.state.value.lower() != request.form['state'].lower():
            new_log = Log(
                customer_id = customer.id,
                state = request.form['state'],
                timestamp = datetime.now(preferred_tz)
            )
            new_log.save_to_db()

        customer.company_name = company_name
        customer.logo = filename
        customer.phone_number = request.form['phone_number']
        customer.address = request.form['address']
        customer.state = request.form['state']

        try:
            customer.save_to_db()
        except:
            return {'message': 'An error occurred while updating a customer'}, 500
                
        return customer.json(), 200


class CustomerListResource(Resource):
    @jwt_required()
    def get(self):
        customers = Customer.query.all()

        return {'customers': [customer.json() for customer in customers]}, 200

