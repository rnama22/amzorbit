import json

from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt_claims

from globalinfo.globalutils import transactions, timing, logger
from globalinfo.routeutils import results, error_handler
from productmanagement.product.service.productservice import ProductService


class ProductSearchController(Resource):

    product_service = ProductService()

    @jwt_required
    @timing
    @transactions
    @error_handler
    def get(self):
        '''
            This controller method is to retrieve the product given anysearch criteria

            As of now, it only retrieves the products for each tenant

        '''

        tenant_id = get_jwt_claims()['tenant_id']
        logger.debug(
            'Post method is invoked to retrieve the products for the tenant {0}'.format(tenant_id))
        product = self.product_service.search({}, tenant_id)
        return results(status="success", message="Fetched Product", data=product, format_json=True)

    @jwt_required
    @timing
    @transactions
    @error_handler
    def post(self):
        '''
            This controller method is to retrieve the product given anysearch criteria

            As of now, it only retrieves the products for each tenant
        '''

        tenant_id = get_jwt_claims()['tenant_id']
        logger.debug(
            'Post method is invoked to retrieve the products for the tenant {0}'.format(tenant_id))
        product = self.product_service.search({}, tenant_id)
        return results(status="success", message="Fetched Products", data=product, format_json=True)
