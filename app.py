''' API End Points/Customer Interaction'''
import os
import json
import yaml
import datetime

from flask import Flask
from flask_cors import CORS
from flask_restful import Resource, Api
from flask_jwt_extended import JWTManager

from scheduler import start_scheduler

from usermanagement.user.controller.usercontroller import UserController
from usermanagement.user.controller.accountcontroller import LoginController
from usermanagement.user.controller.userupdatecontroller import UserUpdateController
from usermanagement.user.controller.passwordupdatecontroller import PasswordUpdateController
from usermanagement.user.controller.tenantupdatecontroller import TenantUpdateController
from usermanagement.user.controller.tenantusersearchcontroller import TenantUserSearchController
from usermanagement.user.controller.inviteusercontroller import InviteUserController
from usermanagement.user.controller.useraccountcontrolloer import UserAccountController
from usermanagement.user.controller.emailvalidatecontroller import EmailValidateController
from usermanagement.user.controller.emailvalidateresendcontroller import EmailValidateResendController
from usermanagement.user.controller.resetpasswordlinkcontroller import ResetPasswordlinkController
from usermanagement.user.controller.resetpasswordcontroller import ResetPasswordController

from productmanagement.alert.controller.alertcontroller import AlertController
from productmanagement.alert.controller.alertupdatecontroller import AlertUpdateController
from productmanagement.product.controller.productcontroller import ProductController
from productmanagement.product.controller.productsearchcontroller import ProductSearchController
from productmanagement.product.controller.productupdatecontroller import ProductUpdateController
from productmanagement.product.controller.productscrapecontroller import ProductScrapeController
from productmanagement.product.controller.productstatuscountcontroller import ProductStatusCountController

from usermanagement.user.controller.paymentcontroller import PaymentController
from usermanagement.user.controller.subscriptioncontroller import SubscriptionController

from globalinfo.globalutils import logger


APP = Flask(__name__)
CORS(APP)
API = Api(APP)

APP.config['JWT_SECRET_KEY'] = ''
APP.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(days=2)
APP.config['JWT_REFRESH_TOKEN_EXPIRES'] = datetime.timedelta(days=30)

jwt = JWTManager(APP)

API.add_resource(ProductController, '/api/product')
API.add_resource(ProductSearchController, '/api/product/search')
API.add_resource(ProductUpdateController, '/api/product/update')
API.add_resource(ProductScrapeController, '/api/product/scrape')
API.add_resource(UserController, '/api/user')
API.add_resource(LoginController, '/api/user/login')
API.add_resource(UserUpdateController, '/api/user/update')
API.add_resource(PasswordUpdateController, '/api/user/updatepassword')
API.add_resource(AlertController, '/api/alert')
API.add_resource(ProductStatusCountController, '/api/product/statuscount')
API.add_resource(AlertUpdateController, '/api/alert/update')
API.add_resource(TenantUpdateController, '/api/tenant')
API.add_resource(PaymentController, '/api/payment')
API.add_resource(SubscriptionController, '/api/subscription')
API.add_resource(InviteUserController, '/api/user/invite')
API.add_resource(UserAccountController, '/api/user/accountcreate')
API.add_resource(EmailValidateController, '/api/user/validateemail')
API.add_resource(EmailValidateResendController,
                 '/api/user/resendvalidationemail')
API.add_resource(ResetPasswordlinkController, '/api/user/resetpasswordlink')
API.add_resource(ResetPasswordController, '/api/user/resetpassword')
API.add_resource(TenantUserSearchController, '/api/user/search')


class PingController(Resource):
    def get(self):
        return {'hello': 'amzorbit'}


API.add_resource(PingController, '/api/ping')


@jwt.user_identity_loader
def user_identity_lookup(acc_user):
    return acc_user.user_id


@jwt.user_claims_loader
def add_claims_to_access_token(acc_user):

    return {
        'tenant_id': acc_user.tenant_id
    }


start_scheduler()

with open('config.yml') as config_input:
    config = yaml.load(config_input)

# Or can import mode from global utils
#mode = os.environ['EnvMode']
mode = 'local'

if __name__ == '__main__':
    logger.info('app is launched')
    APP.run(host=config[mode]['APP_HOST'],
            port=config[mode]['APP_PORT'], debug=True,  threaded=True)
