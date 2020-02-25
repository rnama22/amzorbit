import json
import yaml

from datetime import datetime
from sqlalchemy import func

from process.entity.product.user import User
from process.entity.product.tenant import Tenant
from process.entity.product.alert import Alert
from process.entity.product.product import Product
from process.entity.product.productstatehistory import ProductStateHistory

from process.globalutils import Session, transactions, timing, logger
from process.que.kafkaproducerinput import KafkaProducerInput


class SpyderDataProcess:

    kafka_que = KafkaProducerInput()

    # constants
    # update the same in alerservice too
    alternate_names = {'buyboxSellerName': 'Buy Box',
                       'title': 'Title', 'listItems': 'Bullets', 'images': 'Images',
                       'description': 'Description', 'dimensions': 'Dimensions', 'salesrank': 'Sales Rank',
                       'sellerDescription': 'Seller Description', 'hiRes': 'High Resolution Image',
                       'thumb': 'Thumb Images', 'productDimension': 'Dimensions',
                       'bestSeller': 'Best Seller Tag',
                       'bestSellerRank': 'Best Seller Rank'}

    diff_exclude_fieldlist = ['metaLink', 'metaContent', 'metaTitle', 'metaKeywords', 'metaPageTitle', 'bylineInfo', 'bylineUrl', 'currentReviewRating', 'noOfReviews',
                              'fullfilledBy', 'merchantId', 'sellingCustomerId', 'isMerchantExclusive', 'reviews', 'images', 'buyboxSellerName', 'bestSellerRank']

    image_compare = ['hiRes', 'thumb']
    admin_mobile_num = '7035829800'

    def process(self, output, product):
        '''
        This method to initiate the data processing for the crwaled data
        '''

        logger.info("processing started for the crawled data")
        self.state_update(output, product)

    def aletrnate_names_create(self, attribute):
        ''' 
        Global method to create user friendly names
        '''

        alternate_names = SpyderDataProcess.alternate_names
        if attribute in alternate_names.keys():
            return alternate_names[attribute]

        return attribute

    @transactions
    @timing
    def state_update(self, output, product):
        ''' 
        This method is a handler to compute the diff, updating the product and creating alert
        '''

        session = Session()

        # variables
        diff = {}
        diff['diff'] = {}
        ideal_state = {}
        updated_diffAttributes = []
        diffAttributes = []
        previous_diffAttributes = []

        # retrieving the product info
        # use product id
        product_new = session.query(Product).filter(
            Product.asin == product.asin).filter(
            Product.tenant_id == product.tenant_id).one_or_none()

        logger.info('product health status is {0}'.format(product_new))
        logger.info('product health status is {0}'.format(product_new.asin))

        health_status_previous = product_new.health_status
        logger.info('printing the state_diff {0}'.format(
            product_new.state_diff))

        if product_new.state_diff:
            previous_diffAttributes = json.loads(product_new.state_diff)

        # If the product is newly added load the output to ideal state
        # else compute diffs,create aleters, and send notifications
        if not json.loads(product_new.ideal_state):

            logger.info(
                'Updating the product for the first time: Asin {0}'.format(product_new.asin))

            ideal_state = json.dumps(output)
            product_new.ideal_state = ideal_state
            product_new.current_state = ideal_state
            product_new.title = output['title']
            product_new.update_dt = datetime.utcnow()
            product_new.refresh_dt = datetime.utcnow()
            if output['images']:
                product_new.image = self.find_image(output['images'])

            # buy box check
            if output['buyboxSellerName']:
                buy_box_check = self.buy_box_infocheck(
                    product.tenant_id, output['buyboxSellerName'])
                if not buy_box_check:
                    alternate_name = self.aletrnate_names_create(
                        'buyboxSellerName')
                    diffAttributes.append(alternate_name)
        else:
            logger.info('Updating the details for already exisisting product: Asin {0}'.format(
                product_new.asin))
            product_new.current_state = json.dumps(output)
            product_new.update_dt = datetime.utcnow()
            product_new.refresh_dt = datetime.utcnow()

            # persisting ideal_state
            ideal_state = product_new.ideal_state
            diffAttributes = self.diff_compute(product_new, output)

        if len(diffAttributes) > 0 and product_new.health_status == 'Healthy':
            product_new.state_diff = json.dumps(diffAttributes)
            product_new.health_status = 'Unhealthy'
            self.alert_create(
                product_new, diffAttributes, previous_diffAttributes, 'Unhealthy', 'The following product attributes have changed')

        elif len(diffAttributes) > 0:
            updated_diffAttributes = self.alert_diff_previous(
                product_new.id, product_new.tenant_id, diffAttributes)
            product_new.state_diff = json.dumps(diffAttributes)
            product_new.health_status = 'Unhealthy'

            if len(updated_diffAttributes) > 0:
                self.alert_create(
                    product_new, diffAttributes, previous_diffAttributes, 'Unhealthy', 'The following product attributes have changed')

        else:
            product_new.state_diff = json.dumps(diffAttributes)
            product_new.health_status = 'Healthy'

        # if product_new.health_status == 'Unhealthy':
        # checking previous and current health status
        if health_status_previous == 'Unhealthy' and product_new.health_status == 'Healthy':
            message = 'Great, status changed from Unhealthy to Healthy. The following attributes have been corrected'
            # when the status is changed to healthy, previous_diffattributes have to be sent to the user
            self.alert_create(
                product_new, previous_diffAttributes, None, 'Healthy', message)

        # creating product state history info
        self.product_state_history_create(
            product_new, json.dumps(diffAttributes))

        product_new.product_info_status = 'Updated'

    def find_image(self, output_images):
        '''
            This method is to find the image in the crawled data
            Needs to update to get the image apart from the hi res and thumb nail
        '''

        logger.info('Finding the image for the product')

        for position in range(0, len(output_images)-1):
            for key in output_images[position].keys():
                if key in ['hiRes']:
                    if output_images[position][key] is not None:
                        return output_images[position][key]
        return None

    def diff_compute(self, product, output):
        ''' 
        Handler method to compute diff for attributes, images, and buxbox sellers
        '''

        logger.info('About to compute diffs for the product')
        diffAttributes = []

        # calculating diff for all the attributes
        diffAttributes = self.diff_compute_attributes(
            output, json.loads(product.ideal_state))

        # calcualting diff for the images
        diffImages = self.diff_images(output['images'], json.loads(
            product.ideal_state)['images'])
        if diffImages:
            logger.info('updating images with diffatrributes')
            diffAttributes.extend(diffImages)

        # Check if buy box seller info with the info on tenant settings
        if output['buyboxSellerName']:
            buy_box_check = self.buy_box_infocheck(
                product.tenant_id, output['buyboxSellerName'])
            if not buy_box_check:
                alternate_name = self.aletrnate_names_create(
                    'buyboxSellerName')
                diffAttributes.append(alternate_name)

        return diffAttributes

    def diff_compute_attributes(self, current_state, ideal_state):
        '''
            This method computes the diff by comparing attributes
        '''

        logger.info('computing diff of the attributes')
        diffAttributes = []

        diff_exclude_fieldlist = SpyderDataProcess.diff_exclude_fieldlist

        for key in current_state.keys():
            if key in ideal_state.keys():
                if key not in diff_exclude_fieldlist:
                    if current_state[key] != ideal_state[key]:
                        alternate_key = self.aletrnate_names_create(key)
                        diffAttributes.append(alternate_key)

        return diffAttributes

    def diff_images(self, input_images, output_images):
        '''
        This method is to compute if the images have changed. 

        Currently checks the hires and thumb nail images
        '''
        image_diff = []
        image_compare = SpyderDataProcess.image_compare

        logger.info('computing the diff of the images')

        if len(input_images) < len(output_images):
            image_range = len(input_images)-1
        else:
            image_range = len(output_images)-1
        for position in range(0, image_range):
            input_image_dict = input_images[position]
            if position <= len(output_images)-1:
                output_image_dict = output_images[position]
                for key in input_image_dict.keys():
                    if key in output_image_dict.keys() and key in image_compare:
                        if not input_image_dict[key] == output_image_dict[key]:
                            alternate_key = self.aletrnate_names_create(key)
                            if alternate_key not in image_diff:
                                image_diff.append(alternate_key)
        return image_diff

    def buy_box_infocheck(self, tenant_id, buy_box_name):
        '''
        This method check if the buy box name exists in the tenant settings

        '''

        logger.info('Checking Buy Box Info')
        session = Session()

        tenant = session.query(Tenant).filter(
            Tenant.tenant_id == tenant_id).one_or_none()

        if not tenant.settings:
            return False

        buy_box_names_tenant_list = [name.strip().lower() for name in json.loads(
            tenant.settings)['buy_box_names']]

        if buy_box_names_tenant_list and buy_box_names_tenant_list[0] != "":
            if buy_box_name.strip().lower() in buy_box_names_tenant_list:
                return True
        return False

    @timing
    def alert_diff_previous(self, product_id, tenant_id, diff_attributes):
        '''
        This method is to check if the user was already alerted regarding the diff_Attributes

        Update diff attributes is created based on the previous alert- Adds only the attributes that doesnt exist
        in the previous alert meta data

        '''

        session = Session()

        logger.info('Finding updated diff attributes')

        updated_diff_attributes = []

        sub_query_id = session.query(func.max(Alert.id)).filter(
            Alert.product_id == product_id).filter(Alert.tenant_id == tenant_id)
        latest_alert = session.query(Alert).filter(
            Alert.product_id == product_id).filter(Alert.tenant_id == tenant_id).filter(Alert.id == sub_query_id).one_or_none()

        logger.debug('latest alert is {0}'.format(latest_alert))
        if latest_alert is not None:

            for field in diff_attributes:
                if field not in json.loads(latest_alert.meta_data):
                    updated_diff_attributes.append(field)
                    logger.debug('updated diff attributes are computed {0}'.format(
                        updated_diff_attributes))
            return updated_diff_attributes

        logger.info('updated diff attribues based on alert are {0}'.format(
            updated_diff_attributes))
        return updated_diff_attributes

    def alert_create(self, product, diffAttributes, previous_diffAttributes, alert_type, message):
        '''
        This method ot create the alert
        '''
        logger.info('creating the alert for product {0}'.format(product.asin))
        session = Session()

        alert_info = {'product_id': product.id, 'alert_type': alert_type, 'message': message,
                      'meta_data': json.dumps(diffAttributes), 'status': 'new', 'create_dt': datetime.utcnow(), 'created_by': product.created_by, 'tenant_id': product.tenant_id}

        alert = Alert(**alert_info)

        self.send_notification(product.id,
                               product.created_by, product.tenant_id, product.asin, product.title, diffAttributes, previous_diffAttributes, alert_type, message)

        session.add(alert)
        logger.info('Alert is created')
        return alert

    def product_state_history_create(self, product, diffAttributes):
        '''
        This method to create an entry in the product state history table
        '''
        logger.info('creating product state history entry')

        session = Session()
        product_state_history_info = {'product_id': product.id, 'current_state': product.current_state, 'ideal_state': product.ideal_state,
                                      'state_diff': diffAttributes, 'create_dt': datetime.utcnow(), 'tenant_id': product.tenant_id}
        product_state_history = ProductStateHistory(
            **product_state_history_info)

        session.add(product_state_history)

    def send_notification(self, product_id, user_id, tenant_id, asin, title, diffAttributes, previous_diffAttributes, alert_type, message):
        '''
        This is a handler method to send notifications- email and mobile
        '''

        user_email_list = []
        user_sms_list = []
        selected_attributes_email = []
        selected_attributes_sms = []

        logger.info(
            'working towards sending notifications for the product {0}'.format(asin))

        session = Session()

        # compose user email list and the attributes to be sent for the tenant
        users = session.query(User).filter(User.tenant_id == tenant_id).filter(
            User.email_validation == True).filter(User.email_alert == True).all()
        if users:
            user_email_list, selected_attributes_email = self.compose_contact_list(
                users, diffAttributes, previous_diffAttributes, alert_type, 'e-mail')

        # compose user sms list and attributes to be sent for the tenant
        users = session.query(User).filter(User.tenant_id == tenant_id).filter(
            User.sms_alert == True).all()
        if users:
            user_sms_list, selected_attributes_sms = self.compose_contact_list(
                users, diffAttributes, previous_diffAttributes, alert_type, 'sms')

        # send email to the users under the tenant
        if user_email_list and selected_attributes_email:
            self.send_email(product_id, json.dumps(user_email_list), asin, title,
                            json.dumps(selected_attributes_email), message)

        # send sms to the users under the tenant
        if user_sms_list and selected_attributes_sms:
            self.send_sms(product_id, json.dumps(user_sms_list), asin, title,
                          json.dumps(selected_attributes_sms), message)

    def compose_contact_list(self, users, diffAttributes, previous_diffAttributes, alert_type, contact_type):
        '''
            This method composes the contact list either mobile or e-mail. 

            It only adds the contact info any attributes in diffAttributes,
            if users opts to alert the attribute

        '''

        logger.info('composing contact list to send {0}'.format(contact_type))

        user_contact_list = []
        user_prefered_attributes = []
        user_alert_attributes = []

        for user in users:
            for attribute in diffAttributes:

                # send notfication if they don't have any preference or if the prefered attributes is in diffAttributes
                if not json.loads(user.alert_preference) or attribute in json.loads(user.alert_preference):

                    if previous_diffAttributes and (attribute not in previous_diffAttributes and attribute not in user_prefered_attributes):
                        user_prefered_attributes.append(attribute)

                    # add to contact list only if diffattribute is in user_alert_preference
                    if contact_type == 'e-mail' and user.email_id and user.email_id not in user_contact_list:
                        user_contact_list.append(user.email_id)
                    elif user.mobile_num and user.mobile_num not in user_contact_list:
                        user_contact_list.append(user.mobile_num)

        if alert_type == 'Healthy':
            user_alert_attributes = diffAttributes

        # if any alert attribute is in user prefered attributes, send the whole alert- send all attributes
        if user_prefered_attributes:
            user_alert_attributes = diffAttributes

        return(user_contact_list, user_alert_attributes)

    @timing
    def send_email(self, product_id, email_id_list, asin, title, diffAttributes, message):
        '''
            This method to send alert email info to the kafka que

        '''
        kafka_topic = 'send_email'
        logger.info('sending email')
        alert_info = {'type': 'e-mail', 'product_id': product_id, 'email_id': email_id_list, 'asin': asin, 'title': title, 'message': message,
                      'diffAttributes': diffAttributes}

        self.kafka_producer_que(kafka_topic, alert_info)

    @timing
    def send_sms(self, product_id, mobile_num_list, asin, title, diffAttributes, message):
        '''
        This method is to send sms info to the kafka que
        '''
        kafka_topic = 'send_sms'
        logger.info('sending message')
        alert_info = {'type': 'sms', 'product_id': product_id, 'mobile_num': mobile_num_list,  'asin': asin, 'title': title,
                      'message': message, 'diffAttributes': diffAttributes}
        self.kafka_que.producer_call(kafka_topic, alert_info)

    def send_admin_alert_email(self, ip):
        '''
        This method is to send admin alert via email when the scraping is failing for a particular ip
        '''

        kafka_topic = 'send_email'
        message = 'Error: Scrapping is failing for the IP: {0}, time to resolve it'.format(
            ip)
        alert_info = {'type': 'e-mail', 'email_id': 'admin@leaninnovationlabs.com',
                      'message': message}
        logger.warn('message')
        self.kafka_que.producer_call(kafka_topic, alert_info)

    def send_admin_alert_mobile(self, ip):
        '''
        This method is to send an admin alert via sms when the scraping is failing for a particular ip
        '''

        kafka_topic = 'send_sms'
        message = 'Error: Scrapping is failing for the IP: {0}, time to resolve it'.format(
            ip)
        logger.warn(message)
        alert_info = {'type': 'sms', 'mobile_num': self.admin_mobile_num,
                      'message': message}
        self.kafka_que.producer_call(kafka_topic, alert_info)

    def kafka_producer_que(self, kafka_topic_name, alert_info):
        '''
            This method is to send the topic name and alert info to kafka producer
        '''
        logger.info('alert info being sent to kafka producer')
        self.kafka_que.producer_call(kafka_topic_name, alert_info)
