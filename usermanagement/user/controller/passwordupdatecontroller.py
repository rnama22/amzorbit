import json

from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt_claims

from globalinfo.globalutils import transactions, timing, logger
from globalinfo.routeutils import results, error_handler
from usermanagement.user.service.userservice import UserService


class PasswordUpdateController(Resource):
    user_service = UserService()

    @jwt_required
    @timing
    @transactions
    @error_handler
    def post(self):
        '''
        This method is to update the password
        '''
        account_payload = request.get_json(force=True)
        account_payload['user_id'] = get_jwt_identity()
        logger.info('Post method is called to update the password for the user {0}'.format(
            account_payload['user_id']))
        user = self.user_service.password_update(account_payload)
        return results(status=user[0], message=user[1], data=user[2], format_json=True)
