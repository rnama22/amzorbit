
import json
import requests

from notification.globalutils import ses_client

MAILGUN_API_KEY = 'key-ca3ee1559d3e4426cbca760fdb7832b8'
MAILGUN_DOMAIN_NAME = 'mg.amzorbit.com'


class admin_alert:

    def email_send(self, alert_info):

        print('sending admin alert email')
        print(alert_info)

        RECIPIENT = alert_info['email_id']

        BODY_TEXT = (alert_info['message'])

        # The subject line for the email.
        SUBJECT = "AMZOrbit Alert: Scrapping is Failing"

        BODY_HTML = """<html>
            <head></head
            <body>
                <p>{0}</p>
            </body>
            </html>
                    """.format(alert_info['message'])

        url = 'https://api.mailgun.net/v3/{}/messages'.format(
            MAILGUN_DOMAIN_NAME)
        auth = ('api', MAILGUN_API_KEY)
        data = {
            'from': 'AMZ Orbit <alert@amzorbit.com>',
            'to': RECIPIENT,
            'subject': SUBJECT,
            'text': BODY_TEXT,
            'html': BODY_HTML
        }

        response = requests.post(url, auth=auth, data=data)
        print(response.content)
        response.raise_for_status()
