import json
import uuid
import requests
import yaml

from time import sleep
from random import randint
from sqlalchemy import func
from datetime import datetime

from globalinfo.globalutils import Session, logger, mode
from productmanagement.product.entity.product import Product

from productmanagement.queue.kafkaproducerinput import KafkaProducerInput
from productmanagement.alert.service.alertservice import AlertService
from usermanagement.user.service.userservice import UserService


with open('config.yml') as config_input:
    config = yaml.load(config_input)

MAILGUN_API_KEY = config[mode]['MAILGUN_API_KEY']
MAILGUN_DOMAIN_NAME = config[mode]['MAILGUN_DOMAIN_NAME']


class ProductService:

    kafka_producer = KafkaProducerInput()
    alert_service = AlertService()
    user_service = UserService()

    def add(self, products):
        '''
            This method is to add new product(s) in the db

            It checks if the products exists or archvied earlier.

            If archived, it sets the archive to false

            A few default attributes will be added

            Once the products are added, the product info will be sent to kafka que for further scraping
        '''

        session = Session()

        product_list = []
        ideal_state = {}
        added_products = []
        existing_products = []
        invalid_products = []

        default_input = {'health_status': 'Healthy', 'ideal_state': json.dumps(
            ideal_state), 'product_info_status': 'Pending Update', 'create_dt': datetime.utcnow(), 'created_by': products['user_id'],
            'title': 'Hold Tight! We are Retrieving Product Info', 'archive': False, 'tenant_id': int(products['tenant_id'])}

        for product_info in products['products']:

            if len(product_info['asin'].strip()) == 10:

                default_input['uid'] = str(uuid.uuid1())
                product_info['asin'] = product_info['asin'].strip()

                product_input = {**product_info, **default_input}
                product = Product(**product_input)

                instance = session.query(Product).filter(
                    Product.asin == product.asin).filter(Product.tenant_id == int(products['tenant_id'])).one_or_none()

                archived_product = session.query(Product).filter(
                    Product.asin == product.asin).filter(Product.tenant_id == int(products['tenant_id'])).filter(Product.archive == True).one_or_none()

                if instance == None and archived_product == None:
                    logger.debug(
                        'The product with asin {0} is being added'.format(product_info['asin']))
                    product_list.append(product)
                    added_products.append({'asin': product_info['asin']})

                elif archived_product != None:

                    logger.debug('The product {0} is being retrieved from the archived state'.format(
                        product_info['asin']))

                    archived_product.archive = False
                    session.add(archived_product)

                else:

                    logger.debug('The product {0} already exists'.format(
                        product_info['asin']))

                    existing_products.append(
                        {'asin': product_info['asin'], 'message': 'This asin is already present so ignored'})

                session.add_all(product_list)
                session.commit()

            else:
                logger.info('The given asin {0} is invalid'.format(
                    product_info['asin']))

                invalid_products.append(
                    {'asin': product_info['asin'], 'message': 'Invalid asin length'})

        products_new = session.query(Product).filter(
            Product.product_info_status == 'Pending Update').filter(Product.archive != True).filter(Product.tenant_id == int(products['tenant_id'])).all()

        for instance in products_new:

            logger.info('The product {0} is added and being sent to kafka que for scraping'.format(
                instance.asin))

            self.kafkaproducer_call(self.row2dict(instance))
            # wait for 1-3 seconds for each product
            sleep(randint(1, 3))

        status = {'success': added_products,
                  'warning': existing_products, 'error': invalid_products}
        return status

    def kafkaproducer_call(self, product_info):
        '''
            This method is to pass the product info to the kafka que
        '''
        logger.debug('The product {0} will be sent to kafka producer'.format(
            product_info['asin']))

        self.kafka_producer.producer_call(product_info)

    def row2dict(self, row):
        '''
            This method is to conver a product instance to dict
        '''

        product_dict = {}
        logger.debug(
            'The product {0} instance is being converted to dict'.format(row.asin))
        for column in row.__table__.columns:
            product_dict[column.name] = str(getattr(row, column.name))
        return product_dict

    def search(self, criteria, tenant_id):
        '''
            This method is to filter the products given any criteria

            As of now, it supports only filtering by tenant_id


        '''
        session = Session()

        logger.info(
            'The products for the tenant_id {0} are being retrieved'.format(tenant_id))

        products = session.query(Product).filter(
            Product.archive != True).filter(
            Product.tenant_id == int(tenant_id)).all()

        session.commit()
        return products

    def update(self, product_payload, user_id, tenant_id):
        '''
            This method is to update the product for each given user
        '''

        session = Session()
        product_payload['update_dt'] = datetime.utcnow()
        product_payload['updated_by'] = int(user_id)
        product = Product(**product_payload)

        logger.info('The product {0} with user_id {1} and tenant_id {2} is being updated'.format(
            json.dumps(product_payload['asin']), user_id, tenant_id))

        session.query(Product).filter(
            Product.id == product.id).filter(
            Product.tenant_id == int(tenant_id)).update(product_payload)
        session.commit()

        return self.get(product.id, tenant_id)

    def get(self, productId, tenant_id):
        '''
            This method is to retrieve the product info for the given tenant
        '''

        session = Session()
        logger.info('The product with product_id {0} and tenant_id {1} is being retrieved'.format(
            productId, tenant_id))

        product = session.query(Product).filter(Product.id == productId).filter(
            Product.archive != True).filter(Product.tenant_id == int(tenant_id)).one_or_none()
        session.commit()

        if product == None:
            logger.error('The product with product_id {0} and tenant_id {1} doesnt exist'.format(
                productId, tenant_id))

            return "Product Doesn't Exist"
        else:
            return product

    def delete(self, productId, tenant_id):
        '''
            This method is delete the product for a given tenant

            The product archive status will be set to true rather than deleting the info

        '''

        session = Session()

        logger.info('The product with product_id {0} and tenant_id {1} is being archived'.format(
            productId, tenant_id))

        product_id = {'id': productId}
        product = Product(**product_id)

        product = session.query(Product).filter(
            Product.id == product.id).filter(Product.tenant_id == int(tenant_id)).one_or_none()
        product.archive = True
        session.add(product)
        session.commit()

    def scrape_all(self):
        '''
            This method is to send all the products for scrapping. 

            All the products will be retrieved and sent to kafka que

        '''
        session = Session()
        products = session.query(Product).filter(Product.archive != True).all()
        logger.debug(
            'The products for scraping are retrived and being sent to kafka que')

        for product in products:
            product.product_info_status = 'Verification In Progress'
        session.commit()

        for product in products:

            logger.debug(
                'The product {0} is being sent to kafka que for scraping'.format(product.asin))

            self.kafkaproducer_call(self.row2dict(product))

    def scrape_limited(self, criteria):
        ''' 
            This method is to Scrape Based on Criteria
            The product will be retrieved and sent to kafka by updating product info status

        '''

        session = Session()

        products = session.query(Product).filter(Product.archive != True).filter(
            Product.tenant_id == int(criteria['tenant_id'])).filter(
            Product.id == int(criteria['id'])).all()

        for product in products:
            logger.info('The product {0} for the tenant {1} is being scrapped'.format(
                product.asin, product.tenant_id))
            product.product_info_status = 'Verification In Progress'
        session.commit()

        for product in products:
            self.kafkaproducer_call(self.row2dict(product))

    def status_count(self, tenant_id):
        '''
            This method is to retrieve the healthy status count of the products for each tenant

        '''
        session = Session()

        logger.debug(
            'Product health status count is being retreived for the tenant {0}'.format(tenant_id))

        total_count = session.query(func.count(
            '*')).filter(Product.tenant_id == tenant_id).filter(Product.archive != True).all()
        healthy_count = session.query(func.count(
            '*')).filter(Product.tenant_id == tenant_id).filter(Product.health_status == 'Healthy').filter(Product.archive != True).all()
        unhealthy_count = session.query(func.count(
            '*')).filter(Product.tenant_id == tenant_id).filter(Product.health_status == 'Unhealthy').filter(Product.archive != True).all()

        session.commit()

        product_count = {'total': total_count[0][0],
                         'healthy': healthy_count[0][0],
                         'unhealthy': unhealthy_count[0][0]}
        logger.debug('product healthy status count for the tenant {0} is {1}'.format(
            tenant_id, json.dumps(product_count)))
        return product_count

    def daily_digest_tenant(self, tenant_id):
        '''
        This method is to compose the daily digest for the tenant

        All the products will be retrieved for each tenant

        Alerts in past 24 hours will be retrieved from alert service module

        It will also retrieve the product health count for each tenant

        '''
        session = Session()

        tenant_alerts = []
        products_health_count = self.status_count(tenant_id)

        if products_health_count['total'] == 0:
            return None

        products = session.query(Product).filter(
            Product.archive != True).filter(Product.tenant_id == tenant_id).all()

        for product in products:
            product_alerts = []
            product_summary = {}
            alert_summary = self.alert_service.daily_digest_alerts(
                product.id, product.tenant_id)

            if alert_summary:
                product_alerts.extend(alert_summary)
                product_summary['asin'] = product.asin
                product_summary['title'] = product.title
                product_summary['product_alerts'] = product_alerts
                tenant_alerts.append(product_summary)
            else:
                return None

        return {'alerts': tenant_alerts, 'health_count': products_health_count}

    def daily_digest_formatting(self, tenant_summary):
        '''
            This method is to format the message to send to users
        '''

        alert_summary = []
        products_health_count = tenant_summary['health_count']
        tenant_alerts = tenant_summary['alerts']

        status_summary = 'Total Products: ' + str(products_health_count['total'])+', '+'Healthy Products: ' + \
            str(products_health_count['healthy']) + ', ' + \
            'Unhealthy Products: ' + \
            str(products_health_count['unhealthy']) + '<br/>'

        for product in tenant_alerts:
            product_asin = product['asin']
            product_title = product['title']

            alerts = '.<br/>'.join(product['product_alerts'])
            summary = product_asin + ':  ' +  \
                product_title + '<br/>' + \
                'Alert Summary: <br/>' + '    ' + alerts + '<br/> <br/>'
            alert_summary.append(summary)

        email_body = status_summary + ' <br/>' + \
            '<br/>' + ('<br/>'.join(alert_summary))
        BODY_TEXT = tenant_summary
        BODY_HTML = """<html>
            <head></head
            <body>
                <p>{0}</p>
            </body>
            </html>
                    """.format(email_body)

        return {'text': BODY_TEXT, 'html': BODY_HTML}

    def send_email(self, email_context):
        ''' 
        This method is to send emails using mail gun
        '''

        url = 'https://api.mailgun.net/v3/{}/messages'.format(
            MAILGUN_DOMAIN_NAME)

        auth = ('api', MAILGUN_API_KEY)

        data = {
            'from': 'AMZ Orbit <alert@amzorbit.com>',
            'to': email_context['to'],
            'bcc': email_context['bcc'],
            'subject': email_context['subject'],
            'text': email_context['text'],
            'html': email_context['html']
        }
        response = requests.post(url, auth=auth, data=data)
        response.raise_for_status()

    def daily_digest_task(self):
        '''
            Retrieves tenants from user services- User Module
            Compute the  daily digest for each tenant
            Format the daily digest summary
            Get the user emails for each tenant
            Send email to all the users of the tenant
        '''

        tenants = self.user_service.tenants_all()

        for tenant in tenants:
            email_list = []

            tenant_id = tenant.tenant_id
            tenant_summary = self.daily_digest_tenant(tenant_id)

            # send only if product count is not zero
            if tenant_summary:
                email_context = self.daily_digest_formatting(tenant_summary)
                email_context['subject'] = "AMZOrbit: Daily Digest"
                email_list = self.user_service.users_email_info(tenant_id)
                email_context['bcc'] = email_list
                email_context['to'] = 'admin@leaninnovationlabs.com'

                if email_list:
                    self.send_email(email_context)
                    logger.info(
                        'user email id list is empty for the tenant {0} '.format(tenant_id))
            else:
                logger.info('sending daily digest is ignored')
