import json
import yaml
import pymysql

from kafka import KafkaProducer
from kafka.errors import KafkaError
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base

from globalinfo.globalutils import Session, producer_start, logger
from productmanagement.product.entity.product import Product


class KafkaProducerInput:

    def producer_call(self, product_info):

        logger.info('product info {0} is being sent to the kafka que from the producer'.format(
            product_info['asin']))

        if product_info:

            ack = self.producer.send('product_to_scrape', {
                'product_info': product_info})
            logger.debug(
                'The kafka acknowledgment after sending the message to que {0}'.format(ack))
            try:
                record_metadata = ack.get(timeout=10)
                logger.info(
                    'Record_meta data for kafka que {0}'.format(record_metadata))
            except KafkaError:
                # Decide what to do if produce request failed...
                logger.error('kafka connection error {0}'.format(KafkaError))

                pass
        else:
            logger.debug(
                'The product info is none so could not send it kafka que')

    def __init__(self):
        logger.info('Kafka producer start method is called')
        self.producer = producer_start()
