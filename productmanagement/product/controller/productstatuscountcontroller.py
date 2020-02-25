import json

from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt_claims

from globalinfo.routeutils import results, error_handler
from globalinfo.globalutils import timing, transactions, logger
from productmanagement.product.service.productservice import ProductService


class ProductStatusCountController(Resource):

    product_service = ProductService()

    @jwt_required
    @timing
    @transactions
    @error_handler
    def get(self):
        '''
            This controller method is to retrieve the product health status count

            This requires jwt authentication
        '''
        tenant_id = get_jwt_claims()['tenant_id']

        logger.debug(
            'Get method is invoked to get the products health status for the tenant {0}'.format(tenant_id))

        feed = self.product_service.status_count(tenant_id)
        return results(status="success", message="Fetched the Status Count", data=feed, format_json=True)
