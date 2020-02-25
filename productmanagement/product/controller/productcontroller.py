import json

from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt_claims

from globalinfo.globalutils import transactions, timing, logger
from globalinfo.routeutils import results, error_handler
from productmanagement.product.service.productservice import ProductService


class ProductController(Resource):

    product_service = ProductService()

    @jwt_required
    @timing
    @transactions
    @error_handler
    def get(self):
        '''
        This controller method is to retrieve an existing product

        This needs jwt authentication and retrieves user id and tenant id from it

        It invokes get method in the product service module

        '''
        product_id = request.args.get("product_id")
        tenant_id = get_jwt_claims()['tenant_id']

        logger.debug('Get method is invoked to retrieve a product with product_id {0} and tenant_id {1}'.format(
            product_id, tenant_id))

        product = self.product_service.get(int(product_id), tenant_id)
        return results(status="success", message="Fetched Product", data=product, format_json=True)

    @jwt_required
    @timing
    @transactions
    @error_handler
    def post(self):
        '''
            This controller method is to add a new product

            This needs jwt authentication and retrieves user id and tenant id from it

            It invokes add method in the product service module

        '''
        products = request.get_json(force=True)
        user_info = {'user_id': get_jwt_identity(
        ), 'tenant_id': get_jwt_claims()['tenant_id']}

        logger.debug('Post method is invoked to add a new product {0} by user {1}'.format(
            json.dumps('products'), json.dumps(user_info)))

        products = {**products, **user_info}
        products_info = self.product_service.add(products)

        return results(status="success", message="Added Products", data=products_info, format_json=True)

    @jwt_required
    @timing
    @transactions
    @error_handler
    def delete(self):
        '''
            This controller method is to delete a new product

            This needs jwt authentication and retrieves user id and tenant id from it

            It invokes delete method in the product service module
        '''
        product_id = request.args.get("product_id")
        tenant_id = get_jwt_claims()['tenant_id']

        logger.debug('Delete method is invoked to delete a product with product_id {0} and tenant_id {1}'.format(
            product_id, tenant_id))

        self.product_service.delete(int(product_id), int(tenant_id))
        return results(status="success", message="Deleted Product", data='', format_json=True)
