import os
from flask_restful import Resource, reqparse
from flask import request, make_response
from flask import send_from_directory
from werkzeug.utils import secure_filename

from api.models import Customer, Document
from api.utils.CONST import UPLOAD_FOLDER_DOCUMENT


class DocumentUploadResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('filename', type=str, required=True)

    def post(self, customer_id, name):
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
                
                document.save(os.path.join(UPLOAD_FOLDER_DOCUMENT, filename))

                return new_document.json()
        
        return {'message': 'No document file provided!'}
    
class DocumentDownloadResource(Resource):
    def get(self, customer_id, document_id):
        document = Document.query.filter_by(customer_id=customer_id, id=document_id).first()

        if not document:
            return {'message': 'Document not found!'}, 404
        
        response = make_response(send_from_directory(UPLOAD_FOLDER_DOCUMENT, document.filename, as_attachment=True))
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

