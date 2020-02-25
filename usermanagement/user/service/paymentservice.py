import json
import yaml
import uuid
import bcrypt
import boto3
import stripe
import requests


from datetime import datetime, timedelta
from botocore.exceptions import ClientError
from flask_jwt_extended import create_access_token, create_refresh_token

from globalinfo.globalutils import Session, ses_client, mode, logger
from usermanagement.user.entity.user import User
from usermanagement.user.entity.payment import Payment
from usermanagement.user.entity.subscription import Subscription

with open('config.yml') as config_input:
    config = yaml.load(config_input)

stripe.api_key = "sk_test_nDLahJ4sHOqUSNsJIB6ppc6Y"


class PaymentService:
    ''' This class handles all the methods for payment entity'''

    def get(self, user_id):
        # def get(self,user_id,tenant_id):
        ''' 
            This method retrieves the user info
        '''
        payload = {}
        session = Session()
        card = session.query(Payment).filter(
            Payment.user_id == user_id).one_or_none()
        # subscription = session.query(Subscription).filter(Subscription.tenant_id == tenant_id)
        session.commit()

        payload['cardDetails'] = card

        if card is None:
            logger.error('Card with user_id {0} doesnot exist'.format(
                user_id))
            return ('error', 'Card doesnt exist', None)
        else:
            logger.info('Card info is retreived for the user_id {0} '.format(
                card))

            return ('success', 'Card Info Retrieved', payload)

    def addPayment(self, payload):
        ''' 
            This method is for the payment information insertion. 

        '''
        session = Session()

        default_info = {'create_dt': datetime.utcnow(),
                        'update_dt': datetime.utcnow()}

        payment = payload['payment_payload']

        subscription = payload['subscription']
        plan_id = subscription['plan_id']
        stripe_token = payment['id']
        user_id = payment['user_id']

        logger.info('Payment information is being added for the prospective user with the given user name {0}'.format(
            payment['card']['name']))

        payment_payload = {'last4': payment['card']['last4'], 'brand': payment['card']['brand'],
                           'exp_month': payment['card']['exp_month'], 'exp_year': payment['card']['exp_year'],
                           'name': payment['card']['name'], 'stripe_token': payment['id'], 'user_id': payment['user_id']}

        payment_obj = {**payment_payload, **default_info}
        payment = Payment(**payment_obj)
        session.add(payment)

        plan = session.query(Subscription).filter(
            Subscription.id == plan_id).one_or_none()

        # logger.info('plan id is  {0}'.format(plan.plan_id))

        user = session.query(User).filter(
            User.user_id == user_id).one_or_none()

        user_email_id = user.email_id

        # stripe_token should be a source id

        customer_id = stripe.Customer.create(
            email=user_email_id,
            source=stripe_token,
        )
        logger.info('customer id :{0} '.format(customer_id))

        subscription = stripe.Subscription.create(
            customer=customer_id,
            items=[{'plan': plan.plan_id}],
        )
        # update subscription_expiry to "valid"
        user.suscription_expiry = None
        user.subscription_id = plan.id
        session.add(user)
        session.commit()

        return ('success', 'Payment is Successful', None)

    def get_subscription_plans(self, user_id):
        # def get(self,user_id,tenant_id):
        ''' 
            This method retrieves the user info
        '''
        payload = {}
        session = Session()
        # subscription = session.query(Subscription).filter(Subscription.tenant_id == tenant_id)
        plans = session.query(Subscription).all()
        session.commit()
        payload['plans'] = plans

        if plans is None:
            logger.error("no plans to show")
            return ('error', 'There are no Plans to', None)
        else:
            logger.info('Card info is retreived for the user_id {0} '.format(
                plans))

            return ('success', 'plans Info Retrieved', payload)
