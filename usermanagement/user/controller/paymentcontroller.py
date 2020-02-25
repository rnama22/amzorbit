import json

from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt_claims


from globalinfo.globalutils import transactions, timing, logger
from globalinfo.routeutils import results, error_handler
from usermanagement.user.service.paymentservice import PaymentService


class PaymentController(Resource):

    payment_service = PaymentService()

    @jwt_required
    @timing
    @transactions
    @error_handler
    def post(self):
        '''
            This controller method is to add the user

        '''
        payment_payload = request.get_json(force=True)
        payment_payload['payment_payload']['user_id'] = get_jwt_identity()
        # user_payload['tenant_id'] = get_jwt_claims()['tenant_id']
        logger.info('Post method is called to register the user with the info {0}'.format(
            json.dumps(payment_payload['payment_payload']['user_id'])))
        payment = self.payment_service.addPayment(payment_payload)
        return results(status=payment[0], message=payment[1], data=payment[2], format_json=True)

    @jwt_required
    @timing
    @transactions
    @error_handler
    def get(self):
        '''
            This controller method is to retrieve teh card info
        '''
        user_id = get_jwt_identity()
        tenant_id = get_jwt_claims()['tenant_id']
        logger.info('Card info will be retrieved for the user_id {0} and tenant_id {1}'.format(
            user_id, tenant_id))
        # payment = self.payment_service.get(user_id,tenant_id)
        payment = self.payment_service.get(user_id)
        return results(status=payment[0], message=payment[1], data=payment[2], format_json=True)
