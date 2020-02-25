import json

from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt_claims


from globalinfo.globalutils import transactions, timing, logger
from globalinfo.routeutils import results, error_handler
from usermanagement.user.service.userservice import UserService


class UserController(Resource):

    user_service = UserService()

    @jwt_required
    @timing
    @transactions
    @error_handler
    def get(self):
        '''
            This controller method is to retrieve teh use info

        '''
        user_id = get_jwt_identity()
        tenant_id = get_jwt_claims()['tenant_id']
        logger.info('User info will be retrieved for the user_id {0} and tenant_id {1}'.format(
            user_id, tenant_id))
        user = self.user_service.get(user_id, tenant_id)
        return results(status=user[0], message=user[1], data=user[2], format_json=True)

    @timing
    @transactions
    @error_handler
    def post(self):
        '''
            This controller method is to add the user

        '''

        user_payload = request.get_json(force=True)
        logger.info('Post method is called to register the user with the info {0}'.format(
            json.dumps(user_payload)))
        user = self.user_service.register(user_payload)
        return results(status=user[0], message=user[1], data=user[2], format_json=True)

    @jwt_required
    @timing
    @transactions
    @error_handler
    def delete(self):
        '''
            This controller method is add delete the user

        '''
        user_id = get_jwt_identity()
        logger.info(
            'Delete method is called to delete the user with the id {0}'.format(user_id))
        self.user_service.delete(user_id)
        return results(status="success", message="User is Deleted!", data='', format_json=True)
