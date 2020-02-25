import json

from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt_claims


from globalinfo.globalutils import transactions, timing, logger
from globalinfo.routeutils import results, error_handler
from usermanagement.user.service.userservice import UserService


class ResetPasswordlinkController(Resource):
    user_service = UserService()

    @timing
    @transactions
    @error_handler
    def post(self):
        '''
            This controller method is to send reset password link
        '''
        user_payload = request.get_json(force=True)
        logger.info('Post method is called to register the user with the info {0}'.format(
            json.dumps(user_payload)))
        user = self.user_service.resetpasswordlink(user_payload)
        return results(status=user[0], message=user[1], data=user[2], format_json=True)
