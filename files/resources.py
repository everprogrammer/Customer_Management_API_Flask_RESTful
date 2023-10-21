import os
from flask_restful import Resource, reqparse
from flask import request, make_response
from flask import send_from_directory
# from .models import Customer, Document, Log, User
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from datetime import datetime
from .CONST import preferred_tz

from .models import Customer, Document, Log


class CustomerResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('logo', type= FileStorage, location='files')
    parser.add_argument('phone_number', type=int, required=True)
    parser.add_argument('address', type=str, required=True)
    parser.add_argument('state', type=str, required=True)


    def post(self, company_name):
        data = CustomerResource.parser.parse_args()

        upload_folder = "C:\\Users\\Asus\\Documents\\GitHub\\Customer_Management_API_Flask_RESTful\\uploads"


        customer = Customer.find_by_company_name(company_name)
        if customer:
            return {'message': f"Company ({company_name}) already exists!"}, 400

        if not Customer.is_valid_state(data['state']):
            return {'message': 'Invalid state provided, please provide a valid state'}, 400
        
        filename = None 

        # LOGO UPLOADS
        if 'logo' in request.files:
            logo = request.files['logo']
            if logo:
                if not Customer.allowed_logo_file(logo.filename):
                    return {'message': 'Invalid file type for logo. Allowed types: jpg, jpeg, png'}, 400
                filename = secure_filename(logo.filename)
                logo.save(os.path.join(upload_folder, filename))


        new_customer = Customer(
            company_name= company_name,
            logo=filename,
            phone_number=data['phone_number'],
            address=data['address'],
            state=data['state']
        )


        try:
            new_customer.save_to_db()
        except Exception as e:
            return {'message': f'An error occurred inserting the customer!error{str(e)}'}, 500 
        
        new_log = Log(
            customer_id = new_customer.id,
            state = data['state'],
            timestamp = datetime.now(preferred_tz)
                    )

        try:
            new_log.save_to_db()
        except Exception as e:
            return {'message': f'An error occurred inserting the log!error{str(e)}'}, 500 

        return new_customer.json(), 201
    
    # second one
    # def post(self, company_name):
    #     data = CustomerResource.parser.parse_args()

    #     upload_folder = "C:\\Users\\Asus\\Documents\\GitHub\\Customer_Management_API_Flask_RESTful\\uploads"

    #     customer = Customer.find_by_company_name(company_name)
    #     if customer:
    #         return {'message': f"Company ({company_name}) already exists!"}, 400

    #     if not Customer.is_valid_state(data['state']):
    #         return {'message': 'Invalid state provided, please provide a valid state'}, 400

    #     # Handle logo uploads
    #     logo = data['logo']
    #     if logo:
    #         if not Customer.allowed_logo_file(logo.filename):
    #             return {'message': 'Invalid file type for logo. Allowed types: jpg, jpeg, png'}, 400
    #         filename = secure_filename(logo.filename)
    #         logo.save(os.path.join(upload_folder, filename))
    #     else:
    #         filename = None  # Set filename to None when no logo is provided

    #     new_customer = Customer(
    #         company_name=company_name,
    #         logo=filename,
    #         phone_number=data['phone_number'],
    #         address=data['address'],
    #         state=data['state']
    #     )

    #     try:
    #         new_customer.save_to_db()
    #     except Exception as e:
    #         return {'message': f'An error occurred inserting the customer!error{str(e)}'}, 500

    #     new_log = Log(
    #         customer_id=new_customer.id,
    #         state=data['state'],
    #         timestamp=datetime.now(preferred_tz)
    #     )

    #     try:
    #         new_log.save_to_db()
    #     except Exception as e:
    #         return {'message': f'An error occurred inserting the log!error{str(e)}'}, 500

    #     return new_customer.json(), 201

    def get(self, company_name):
        customer = Customer.find_by_company_name(company_name)

        if customer:
            return customer.json(), 200
        return {'message': f'Customer ({company_name}) was not found!'}, 404
    

    def delete(self, company_name):
        customer = Customer.find_by_company_name(company_name)

        if customer:
            customer.delete_from_db()
        return {'message': 'Customer deleted successfully'}, 200
    
    
    def put(self, company_name):
        data = CustomerResource.parser.parse_args()
        customer = Customer.find_by_company_name(company_name)

        upload_folder = "C:\\Users\\Asus\\Documents\\GitHub\\Customer_Management_API_Flask_RESTful\\uploads"

        if not customer:
            return {'message': f'Customer ({company_name}) was not found!'}, 404

        if not Customer.is_valid_state(data['state']):
            return {'message': 'Invalid state provided, please provide a valid state'}, 400
        
        filename = customer.logo
        if 'logo' in request.files:
            logo = request.files['logo']
            if logo:
                if not Customer.allowed_logo_file(logo.filename):
                    return {'message': 'Invalid file type for logo. Allowed types: jpg, jpeg, png'}, 400
                filename = secure_filename(logo.filename)
                logo.save(os.path.join(upload_folder, filename))
            else:
                filename = None
        else:
            filename = None


        if customer.state.value.lower() != data['state'].lower():
            new_log = Log(
                customer_id = customer.id,
                state = data['state'],
                timestamp = datetime.now(preferred_tz)
            )
            new_log.save_to_db()

        customer.company_name = company_name
        customer.logo = filename
        customer.phone_number = data['phone_number']
        customer.address = data['address']
        customer.state = data['state']

        try:
            customer.save_to_db()
        except:
            return {'message': 'An error occurred while updating a customer'}, 500
                
        return customer.json(), 200


class CustomerListResource(Resource):
    def get(self):
        customers = Customer.query.all()

        return {'customers': [customer.json() for customer in customers]}


class DocumentUploadResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('filename', type=str, required=True)

    def post(self, customer_id, name):
        upload_folder = "C:\\Users\\Asus\\Documents\\GitHub\\Customer_Management_API_Flask_RESTful\\uploads"

        # data = DocumentResource.parser.parse_args()
        customer = Customer.find_by_company_id(customer_id)

        if not customer:
            return {'message': 'Customer not found!'}, 404
        
        # FILE UPLOAD
        if 'document' in request.files:
            document = request.files['document']

            if document:
                if not Document.allowed_document_file(document.filename):
                    return {'message': 'Invalid file type for document'}, 400
                
                filename = secure_filename(document.filename)

                new_document = Document(
                    name=name,
                    filename=filename,
                    customer_id=customer_id
                )

                try:
                    new_document.save_to_db()
                except:
                    return {'message': 'An error occurred inserting the document!'}, 500
                
                document.save(os.path.join(upload_folder, filename))

                return new_document.json()
        
        return {'message': 'No document file provided!'}
    
class DocumentDownloadResource(Resource):
    def get(self, customer_id, document_id):
        document = Document.query.filter_by(customer_id=customer_id, id=document_id).first()

        if not document:
            return {'message': 'Document not found!'}, 404
        
        upload_folder = "C:\\Users\\Asus\\Documents\\GitHub\\Customer_Management_API_Flask_RESTful\\uploads"

        response = make_response(send_from_directory(upload_folder, document.filename, as_attachment=True))
        response.headers['Content-Disposition'] = f'attachment; filename={document.filename}'

        return response 
    
        

class DocumentDeleteResource(Resource):
    def delete(self, customer_id, document_id):
        document = Document.query.filter_by(customer_id=customer_id, id=document_id).first()

        if document:
            document.delete_from_db()
            return {'message': 'Document deleted successfully!'}, 200
        return {'message': 'Document not found!'}, 404



class DocumentListResource(Resource):
    def get(self, customer_id):
        documents = Document.query.filter_by(customer_id=customer_id)

        return [document.json() for document in documents]

class LogResource(Resource):

    def get(self, customer_id):
        # customer = Customer.find_by_company_id(customer_id)

        logs = Log.query.filter_by(customer_id=customer_id)

        return [log.json() for log in logs]





        
        
