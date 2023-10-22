import os
from flask_restful import Resource, reqparse
from flask import request, make_response
from flask import send_from_directory
# from .models import Customer, Document, Log, User
from werkzeug.utils import secure_filename
from datetime import datetime
from api.utils.CONST import preferred_tz

from api.models import Customer, Document, Log

class LogResource(Resource):

    def get(self, customer_id):
        # customer = Customer.find_by_company_id(customer_id)

        logs = Log.query.filter_by(customer_id=customer_id)

        return [log.json() for log in logs]


        

