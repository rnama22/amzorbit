import json

from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt_claims

from globalinfo.routeutils import results, error_handler
from globalinfo.globalutils import timing, transactions, logger
from productmanagement.alert.service.alertservice import AlertService


class AlertController(Resource):

    alert_service = AlertService()

    @jwt_required
    @timing
    @transactions
    @error_handler
    def get(self):
        '''
            This controller method is to retrieve all the alerts for the given tenant
        '''
        tenant_id = get_jwt_claims()['tenant_id']
        logger.info(
            'Get method is called to retrieve all the alerts for the tenant {0}'.format(tenant_id))
        alert = self.alert_service.search({}, tenant_id)
        return results(status="success", message="Fetched Alert", data=alert, format_json=True)

    @jwt_required
    @timing
    @transactions
    @error_handler
    def post(self):
        '''
            This controller method is to retrieve all the alerts for the given tenant
        '''
        criteria = request.get_json(force=True)
        tenant_id = get_jwt_claims()['tenant_id']
        logger.info(
            'Post method is called to retrieve all the alerts for the tenant {0}'.format(tenant_id))
        alert = self.alert_service.search(criteria, tenant_id)
        return results(status="success", message="Fetched Alert", data=alert, format_json=True)
