import json

from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt_claims

from globalinfo.globalutils import transactions, timing, logger
from globalinfo.routeutils import results, error_handler
from usermanagement.user.service.userservice import UserService


class TenantUpdateController(Resource):
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
        tenant = self.user_service.tenant_get(tenant_id)
        return results(status=tenant[0], message=tenant[1], data=tenant[2], format_json=True)

    @jwt_required
    @timing
    @transactions
    @error_handler
    def post(self):
        '''
        This controller method is to update the tenant info
        '''
        tenant_payload = request.get_json(force=True)
        tenant_id = get_jwt_claims()['tenant_id']
        logger.info('Post method is called update the tenant info {0} for the id {1}'.format(
            json.dumps(tenant_payload), tenant_id))
        tenant = self.user_service.tenant_update(tenant_id, tenant_payload)
        return results(status=tenant[0], message=tenant[1], data=tenant[2], format_json=True)
