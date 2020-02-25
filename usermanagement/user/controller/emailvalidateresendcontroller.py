import json

from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt_claims


from globalinfo.globalutils import transactions, timing, logger
from globalinfo.routeutils import results, error_handler
from usermanagement.user.service.userservice import UserService


class EmailValidateResendController(Resource):
    ''' 
    This method is to controll the user login 
    '''
    user_service = UserService()

    @jwt_required
    @timing
    @transactions
    @error_handler
    def get(self):
        user_id = get_jwt_identity()
        tenant_id = get_jwt_claims()['tenant_id']
        logger.info('Post method is called to validate the e-mail')
        user = self.user_service.validate_email_resend(user_id, tenant_id)
        return results(status=user[0], message=user[1], data=user[2], format_json=True)
