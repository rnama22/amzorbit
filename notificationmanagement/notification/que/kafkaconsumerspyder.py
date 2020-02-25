import json
import yaml
import scrapy
import requests
import pprint


from notification.globalutils import consumer_start, logger

from notification.email.send_email import Send_Email
from notification.sms.send_sms import Send_Sms


class KafkaConsumerSpyder:

    email = Send_Email()
    sms = Send_Sms()

    def kafka_consumer_start(self):
        '''
        This is kafka consumer for multiple topics

        Multiple types of info is received and will be processed as per the type- e-mail/sms as of now
        '''

        for message in self.consumer:
            alert_info = message.value['alert_info']
            logger.info(
                'message is received from the kafka que- info:{0}'.format(json.dumps(alert_info)))
            if alert_info['type'] == 'e-mail':
                self.email.email_send(alert_info)
            if alert_info['type'] == 'sms':
                self.sms.sms_send(alert_info)

    def __init__(self):
        self.consumer = consumer_start()
