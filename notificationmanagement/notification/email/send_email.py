
import json
import requests

from notification.globalutils import logger

MAILGUN_API_KEY = 'key-ca3ee1559d3e4426cbca760fdb7832b8'
MAILGUN_DOMAIN_NAME = 'mg.amzorbit.com'


class Send_Email:

    def email_send(self, alert_info):
        '''
            This method is to email the alerts
        '''

        logger.info(
            'Alert with is being emailed- Info:{0}'.format(json.dumps(alert_info)))

        attributes = []

        RECIPIENT = json.loads(alert_info['email_id'])

        if 'asin' in alert_info:
            info = 'Product Information ' + \
                ' Asin: {0}  \
                Title: {1} '.format(
                    alert_info['asin'], alert_info['title'])

            attributes = ', '.join(json.loads(
                alert_info['diffAttributes']))

            message = alert_info['message'] + ":" + \
                ' {0}'.format(attributes)

            amazon_link = 'https://www.amazon.com/dp/{0}'.format(
                alert_info['asin'])

            amazon_orbit_link = 'https://app.amzorbit.com/#/product/{0}'.format(
                alert_info['product_id'])

            links = '<a href ="{0}"> View On AmzOrbit </a> &nbsp;&nbsp; <a href="{1}">View On Amazon </a>'.format(
                amazon_orbit_link, amazon_link)

            BODY_TEXT = (message)

            # The subject line for the email.
            SUBJECT = "Alert: {0} {1} {2}".format(
                alert_info['asin'], alert_info['title'], ''.join(attributes))

            BODY_HTML = """<html>
                <head></head
                <body>
                    <p><b>ASIN:</b> {0}</p>
                    <p><b>TITLE:</b> {1}</p>
                    <p>{2}</p>
                    <p>{3}</p>
                </body>
                </html>
                        """.format(alert_info['asin'], alert_info['title'], message, links)
        else:
            SUBJECT = alert_info['message']
            BODY_TEXT = alert_info['message']
            BODY_HTML = alert_info['message']

        url = 'https://api.mailgun.net/v3/{}/messages'.format(
            MAILGUN_DOMAIN_NAME)
        auth = ('api', MAILGUN_API_KEY)
        data = {
            'from': 'AMZ Orbit <alert@amzorbit.com>',
            'to': 'AMZ Orbit <alert@amzorbit.com>',
            'bcc': RECIPIENT,
            'subject': SUBJECT,
            'text': BODY_TEXT,
            'html': BODY_HTML
        }

        response = requests.post(url, auth=auth, data=data)
        logger.info('Response from mailgun for the alert that is sent {0}'.format(
            response.content))
        response.raise_for_status()
