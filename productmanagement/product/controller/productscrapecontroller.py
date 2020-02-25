import json

from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt_claims

from globalinfo.globalutils import transactions, timing, logger
from globalinfo.routeutils import results, error_handler
from productmanagement.product.service.productservice import ProductService


class ProductScrapeController(Resource):

    product_service = ProductService()

    @jwt_required
    @timing
    @transactions
    @error_handler
    def post(self):
        '''
        This controller method is invoke scrapping for a product product

        '''

        product_criteria = request.get_json(force=True)
        user_info = {'tenant_id': get_jwt_claims()['tenant_id']}

        logger.debug('Post method is invoked to scrape the product {0} with the user info {1}'.format(
            json.dumps(product_criteria), json.dumps(user_info)))

        criteria = {**product_criteria, **user_info}
        self.product_service.scrape_limited(criteria)
        return results(status="success", message="Scraping Initiated", data='', format_json=True)
