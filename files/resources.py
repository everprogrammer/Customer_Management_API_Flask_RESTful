import os
from flask_restful import Resource, reqparse
from flask import request
# from .models import Customer, Document, Log, User
from werkzeug.utils import secure_filename


class CustomerResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('company_name', type=str, required=True)
    parser.add_argument('logo', type=str, required=False)
    parser.add_argument('phone_number', type=int, required=True)
    parser.add_argument('address', type=str, required=True)
    parser.add_argument('state', type=str, required=True)

    def post(self):
        from .models import Customer
        data = CustomerResource.parser.parse_args()

        customer = Customer.find_by_company_name(data['company_name'])
        if customer:
            return {'message': f"Company ({data['company_name']}) already exists!"}, 400

        if not Customer.is_valid_state(data['state']):
            return {'message': 'Invalid state provided, please provide a valid state'}, 400
        
        # LOGO UPLOADS
        logo = request.files['logo']
        if logo:
            if not Customer.allowed_logo_file(logo.filename):
                return {'message': 'Invalid file type for logo. Allowed types: jpg, jpeg, png'}, 400
            filename = secure_filename(logo.filename)
            logo.save(os.path.join('uploads/photos', filename))
        else:
            filename = None

 
        new_customer = Customer(
            company_name=data['company_name'],
            logo=filename,
            phone_number=data['phone_number'],
            address=data['address'],
            state=data['state']
        )

        try:
            new_customer.save_to_db()
        except:
            return {'message': 'An error occurred inserting the customer!'}, 500 

        return new_customer.json(), 201
    

    def get(self, company_name):
        from .models import Customer
        customer = Customer.find_by_company_name(company_name)

        if customer:
            return customer.json(), 200
        return {'message': f'Customer ({company_name}) was not found!'}, 404
    

    def delete(self, company_name):
        from .models import Customer
        customer = Customer.find_by_company_name(company_name)

        if customer:
            customer.delete_from_db()
        return {'message': 'Customer deleted successfully'}, 200
    
    
    def put(self, company_name):
        from .models import Customer
        data = CustomerResource.parser.parse_args()
        customer = Customer.find_by_company_name(data['company_name'])

        if not customer:
            return {'message': f'Customer ({company_name}) was not found!'}, 404

        if not Customer.is_valid_state(data['state']):
            return {'message': 'Invalid state provided, please provide a valid state'}, 400
        
        filename = customer.logo
        logo = request.files['logo']
        if logo:
            if not Customer.allowed_logo_file(logo.filename):
                return {'message': 'Invalid file type for logo. Allowed types: jpg, jpeg, png'}, 400
            filename = secure_filename(logo.filename)
            logo.save(os.path.join('uploads/photos', filename))

        customer.company_name = data['company_name']
        customer.logo = filename
        customer.phone_number = data['phone_number']
        customer.address = data['address']
        customer.state = data['state']

        try:
            customer.save_to_db()
        except:
            return {'message': 'An error occurred while updating a customer'}, 500
        
        return customer.json(), 200





        
        
