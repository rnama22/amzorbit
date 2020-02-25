import json

from flask import request
from flask_restful import Resource

from globalinfo.globalutils import transactions, timing, logger
from globalinfo.routeutils import results, error_handler
from usermanagement.user.service.userservice import UserService


class LoginController(Resource):
    ''' 
    This method is to controll the user login 
    '''

    user_service = UserService()

    @timing
    @transactions
    @error_handler
    def post(self):
        account_payload = request.get_json(force=True)
        logger.info('Post method is called to autehnticate the use')
        user = self.user_service.authenticate_user(account_payload)
        return results(status=user[0], message=user[1], data=user[2], format_json=True)
