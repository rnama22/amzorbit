import json
import yaml
import pymysql

from kafka import KafkaProducer
from kafka.errors import KafkaError
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base

from process.globalutils import Session, producer_start, logger


class KafkaProducerInput:

    def producer_call(self, kafka_topic_name, alert_info):
        '''
        This is method to send the info to kafka que
        '''

        if alert_info:

            ack = self.producer.send(kafka_topic_name, {
                'alert_info': alert_info})

            try:
                record_metadata = ack.get(timeout=10)
            except KafkaError:
                # Decide what to do if produce request failed...
                logger.info(
                    'Alert info is sent to kafka que- Ack:{0}'.format(ack))

                pass
        else:
            logger.error('Alert info is None and cannot be sent to kafka que')

    def __init__(self):
        self.producer = producer_start()
