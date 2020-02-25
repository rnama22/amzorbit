import json

from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt_claims


from globalinfo.globalutils import transactions, timing, logger
from globalinfo.routeutils import results, error_handler
from usermanagement.user.service.userservice import UserService


class UserUpdateController(Resource):

    user_service = UserService()

    @jwt_required
    @timing
    @transactions
    @error_handler
    def post(self):
        '''
            This controller method is to update the user info
        '''

        user_payload = request.get_json(force=True)
        user_payload['user_id'] = get_jwt_identity()
        user_payload['tenant_id'] = get_jwt_claims()['tenant_id']

        logger.info('Post method is called to update the user info for the user_id {0} and tenant_id {1}'.format(
            user_payload['user_id'], user_payload['tenant_id']))

        user = self.user_service.update(user_payload)
        return results(status=user[0], message=user[1], data=user[2], format_json=True)
