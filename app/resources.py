import os
from flask_restful import Resource, reqparse
from flask import request
from .models import Customer, Document, Log, User
from werkzeug.utils import secure_filename
from .config import db


class CustomerResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('company_name', type=str, required=True)
    parser.add_argument('logo', type=str, required=False)
    parser.add_argument('phone_number', type=int, required=True)
    parser.add_argument('address', type=str, required=True)
    parser.add_argument('state', type=str, required=True)

    def post(self):
        data = CustomerResource.parser.parse_args()
        company_name = data['name']
        logo = request.files['logo']
        phone_number = data['phone_number']
        address = data['address']
        state = data['state']
        filename= None

        customer = Customer.find_by_company_name(company_name)
        if customer:
            return {'message': f'Company ({company_name}) already exists!'}, 400

        if not Customer.is_valid_state(state):
            return {'message': 'Invalid state provided, please provide a valid state'}, 400
        
        if logo and Customer.allowed_logo_file(logo.filename):
            filename = secure_filename(logo.filename)
            logo.save(os.path.join('uploads/photos', filename))
 
        new_customer = Customer(
            company_name=company_name,
            logo=filename,
            phone_number=phone_number,
            address=address,
            state=state
        )

        db.session.add(new_customer)
        db.session.commit()

        return {'message': f'Company ({company_name}) created successfully!'}, 201
    

        
        
