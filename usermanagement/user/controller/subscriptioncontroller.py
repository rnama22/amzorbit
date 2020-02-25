import json

from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt_claims


from globalinfo.globalutils import transactions, timing, logger
from globalinfo.routeutils import results, error_handler
from usermanagement.user.service.paymentservice import PaymentService


class SubscriptionController(Resource):
    payment_service = PaymentService()

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
        logger.info('Subscription info will be retrieved for the user_id {0} and tenant_id {1}'.format(
            user_id, tenant_id))
        # subscription = self.payment_service.get_subscription_plans(user_id,tenant_id)
        subscription = self.payment_service.get_subscription_plans(user_id)
        return results(status=subscription[0], message=subscription[1], data=subscription[2], format_json=True)
