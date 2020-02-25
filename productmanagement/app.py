''' API End Points/Customer Interaction'''
import datetime
import json

from flask import Flask
from flask_cors import CORS
from flask_restful import Resource, Api
from flask_jwt_extended import JWTManager

from scheduler import start_scheduler

from usermanagement.user.controller.usercontroller import UserController
from usermanagement.user.controller.accountcontroller import LoginController
from usermanagement.user.controller.userupdatecontroller import UserUpdateController
from usermanagement.user.controller.passwordupdatecontroller import PasswordUpdateController


from productmanagement.alert.controller.alertcontroller import AlertController
from productmanagement.alert.controller.alertupdatecontroller import AlertUpdateController
from productmanagement.product.controller.productcontroller import ProductController
from productmanagement.product.controller.productsearchcontroller import ProductSearchController
from productmanagement.product.controller.productupdatecontroller import ProductUpdateController
from productmanagement.product.controller.productscrapecontroller import ProductScrapeController
from productmanagement.product.controller.productstatuscountcontroller import ProductStatusCountController

APP = Flask(__name__)
CORS(APP)
API = Api(APP)

APP.config['JWT_SECRET_KEY'] = 'notsoeasy2break'
APP.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=2)
APP.config['JWT_REFRESH_TOKEN_EXPIRES'] = datetime.timedelta(days=30)

jwt = JWTManager(APP)

API.add_resource(ProductController, '/api/product')
API.add_resource(ProductSearchController, '/api/productsearch')
API.add_resource(ProductUpdateController, '/api/productupdate')
API.add_resource(ProductScrapeController, '/api/productscrape')
API.add_resource(UserController, '/api/user')
API.add_resource(LoginController, '/api/user/login')
API.add_resource(UserUpdateController, '/api/user/update')
API.add_resource(PasswordUpdateController, '/api/user/password/update')
API.add_resource(AlertController, '/api/alert')
API.add_resource(ProductStatusCountController, '/api/product/statuscount')
API.add_resource(AlertUpdateController, '/api/alertupdate')


@jwt.user_identity_loader
def user_identity_lookup(acc_user):
    return acc_user.user_id


@jwt.user_claims_loader
def add_claims_to_access_token(acc_user):

    return {
        'tenant_id': acc_user.tenant_id
    }


start_scheduler()

if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=8082, debug=True,  threaded=True)
