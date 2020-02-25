import json

from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt_claims

from globalinfo.routeutils import results, error_handler
from globalinfo.globalutils import timing, transactions, logger
from productmanagement.alert.service.alertservice import AlertService


class AlertUpdateController(Resource):

    alert_service = AlertService()

    @jwt_required
    @timing
    @transactions
    @error_handler
    def post(self):
        '''
        This controller method is to update the alert for the given criteria and tenant
        '''
        alert_payload = request.get_json(force=True)
        user_id = get_jwt_identity()
        tenant_id = get_jwt_claims()['tenant_id']
        logger.debug('Post method to update the alert with paylod {0} for the user {1} and tenant {2} is invoked'.format(
            json.dumps(alert_payload), user_id, tenant_id))
        self.alert_service.update(alert_payload, user_id, tenant_id)
        return results(status="success", message="Alert Updated Successfully!", data='', format_json=True)
