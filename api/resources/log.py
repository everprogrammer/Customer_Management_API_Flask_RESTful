from flask_restful import Resource
from api.models import Log


class LogResource(Resource):
    def get(self, customer_id):

        logs = Log.query.filter_by(customer_id=customer_id)

        return [log.json() for log in logs]


        

