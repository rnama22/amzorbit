import json

from flask import request
from flask_restful import Resource
from sqlalchemy.ext.declarative import DeclarativeMeta
from flask_jwt_extended import get_jwt_identity, create_access_token, create_refresh_token

from globalinfo.globalutils import transactions, timing, logger
from globalinfo.routeutils import results, error_handler
from usermanagement.user.service.userservice import UserService


class GETJWToken(Resource):

    user_service = UserService()

    @timing
    @transactions
    @error_handler
    def post(self):
        '''
        This method is to generate jwt token for the given payload
        '''
        jwt_payload = request.get_json(force=True)

        logger.info(
            'JWT token is being generated for the info {0}'.format(jwt_payload))

        jwt_token = self.user_service.authenticate_user(jwt_payload)
        return results(status="success", message="Feteched JWT Token", data=jwt_token, format_json=True)


class GETJWTRefreshtoken(Resource):

    user_service = UserService()

    def post(self):
        current_user_name = get_jwt_identity()
        refreshed_jwt_token = self.user_service.jwt_token_refresh(
            current_user_name)
        return results(status="success", message="Fetched Refreshed JWT Token", data=refreshed_jwt_token, format_json=True)
