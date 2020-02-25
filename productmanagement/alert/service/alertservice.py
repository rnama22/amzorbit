import json

from datetime import datetime, timedelta
from sqlalchemy import func

from productmanagement.alert.entity.alert import Alert
from globalinfo.globalutils import Session, logger


class AlertService:

    # always retrive the udpated version from spyderdataprocess.py
    alternate_names = {'buyboxSellerName': 'Buy Box',
                       'title': 'Title', 'listItems': 'Bullets', 'images': 'Images',
                       'description': 'Description', 'dimensions': 'Dimensions', 'salesrank': 'Sales Rank',
                       'sellerDescription': 'Seller Description', 'hiRes': 'High Resolution Image',
                       'thumb': 'Thumb Images', 'productDimension': 'Dimensions',
                       'bestSeller': 'Best Seller Tag',
                       'bestSellerRank': 'Best Seller Rank'}

    def search(self, criteria, tenant_id):
        '''
            This method to retreive the alerts for a given tenant and product
            alert will be sent along with the product info
        '''
        session = Session()

        logger.info(
            'alerts are being retreived for the given tenant and product info')

        query = 'SELECT alert.*, product.title, product.image, product.asin FROM alert, product where alert.product_id = product.id'

        if(criteria != None and 'product_id' in criteria and criteria['product_id'] != None):
            query = query + ' and alert.product_id = ' + \
                str(criteria['product_id'])

        if 'status' in criteria and (criteria['status'] != None):
            query = query + \
                ' and alert.status ="{0}" '.format(
                    str(criteria['status']))

        query = query + ' and alert.tenant_id = ' + \
            str(tenant_id) + ' order by alert.create_dt desc limit 100'
        alert = session.execute(query, {})
        session.commit()
        alerts = []

        for row in alert:
            alerts.append({
                'status': row.status,
                'id': row.id,
                'alert_type': row.alert_type,
                'status': row.status,
                'create_dt': str(row.create_dt),
                'title': row.title,
                'asin': row.asin,
                'image': row.image,
                'product_id': row.product_id,
                'meat_data': row.meta_data,
                'tenant_id': row.tenant_id
            })
        return alerts

    def update(self, alert_payload, user_id, tenant_id):
        '''
        This method is update the alert with the given info
        '''
        session = Session()

        logger.debug('Updating the alerts')

        alert_payload['update_dt'] = datetime.utcnow()
        alert_payload['updated_by'] = int(user_id)
        alert = Alert(**alert_payload)

        session.query(Alert).filter(Alert.id == alert.id).filter(
            Alert.tenant_id == alert.tenant_id).update(alert_payload)

        session.commit()
        return 'Alert Status Updated'

    def daily_digest_alerts(self, product_id, tenant_id):
        '''
            This method is to retrieve the alerts in the past 1 day for a given product and tenant
        '''

        session = Session()
        alert_messages = []

        logger.info('The alerts are being retreived for the product_id {0} and tenant_id {1}'.format(
            product_id, tenant_id))

        alerts = session.query(Alert).filter(
            Alert.product_id == product_id).filter(
            Alert.tenant_id == tenant_id).filter(Alert.create_dt >= datetime.utcnow() - timedelta(days=1)).all()

        if alerts:
            for alert in alerts:
                logger.debug('The alert message is {0}'.format(alert.message))
                diff_attributes = []
                if alert.message:
                    if alert.meta_data:
                        attributes = json.loads(alert.meta_data)
                        for attribute in attributes:
                            updated_attribute = self.aletrnate_names_create(
                                attribute)
                            diff_attributes.append(updated_attribute)

                    alert_info = alert.message + ' : ' + \
                        ', '.join(diff_attributes)
                    alert_messages.append(alert_info)

            logger.info('alert_messages:{0}'.format(alert_messages))
        if not alert_messages:
            return None
        return alert_messages

    def aletrnate_names_create(self, attribute):
        '''
         This is a global method to create user friendly names
         '''

        logger.info(
            'Retrieving the alternate user friendly name for the attribute {} in the alert module'.format(attribute))

        alternate_names = AlertService.alternate_names
        if attribute in alternate_names.keys():
            return alternate_names[attribute]

        return attribute
