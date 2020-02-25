import json

from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt_claims

from globalinfo.globalutils import transactions, timing, logger
from globalinfo.routeutils import results, error_handler
from usermanagement.user.service.userservice import UserService


class TenantUserSearchController(Resource):
    ''' Login '''

    user_service = UserService()

    @jwt_required
    @timing
    @transactions
    @error_handler
    def get(self):
        '''
        This controller method is to retrieve the tenant info
        '''
        tenant_id = get_jwt_claims()['tenant_id']
        logger.info(
            'Get method is called to retrieve the tenant info for the id {0}'.format(tenant_id))
        tenant = self.user_service.users_list_tenant(tenant_id)
        return results(status=tenant[0], message=tenant[1], data=tenant[2], format_json=True)
