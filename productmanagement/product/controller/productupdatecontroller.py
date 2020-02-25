import json

from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt_claims

from globalinfo.globalutils import transactions, timing, logger
from globalinfo.routeutils import results, error_handler
from productmanagement.product.service.productservice import ProductService


class ProductUpdateController(Resource):

    product_service = ProductService()

    @jwt_required
    @timing
    @transactions
    @error_handler
    def post(self):
        '''
            This controller is to update the product info for a given user

        '''

        product_payload = request.get_json(force=True)
        user_id = get_jwt_identity()
        tenant_id = get_jwt_claims()['tenant_id']

        logger.debug('Post method is invoked to update the product{0} with user info{1}'.format(
            json.dumps(product_payload), json.dumps(tenant_id)))
        product = self.product_service.update(
            product_payload, user_id, tenant_id)
        return results(status="success", message="Updated Product", data=product, format_json=True)
