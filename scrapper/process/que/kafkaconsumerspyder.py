import json
import yaml
import scrapy
import requests
import pprint
from random import randint
from time import sleep

from process.entity.product.product import Product
from process.globalutils import consumer_start, logger
from process.dataprocess.spyderdataprocess import SpyderDataProcess
from process.spyder.spyder import Spyder


class KafkaConsumerSpyder:
    skp = SpyderDataProcess()
    spyder = Spyder()

    IP_GC = ['35.202.233.70', '35.224.14.120', '35.202.198.195',
             '35.202.188.75', '35.226.146.46', '35.224.73.57']

    BAD_IP = []

    def kafka_consumer_start(self):
        '''
        This method is to retrive the info from the kafka que

        Retrieves the info and info is sent to spyder data process
        '''
        logger.info('kafka consumer started')
        for message in self.consumer:
            product_info = message.value['product_info']
            product = Product(**product_info)
            data = self.spyder.crawl(product)

            if data and data['title']:
                sleep(randint(3, 8))
                self.skp.process(data, product)
            elif data is None or 'ip' in data:
                if data['ip'] not in self.BAD_IP:
                    self.BAD_IP.append(data['ip'])
                    self.skp.send_admin_alert_email(data['ip'])
                    self.skp.send_admin_alert_mobile(data['ip'])

    def __init__(self):
        self.consumer = consumer_start()
