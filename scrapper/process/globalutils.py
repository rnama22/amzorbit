import os
import yaml
import time
import json
import pymysql
import logging
import logging.handlers
import traceback


from kafka import KafkaProducer, KafkaConsumer
from kafka.errors import KafkaError
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from functools import wraps
from .exceptions import *


IP_GC = ['35.232.20.198', '35.192.213.15', '35.232.104.178',
         '35.226.235.168', '35.224.236.129', '35.202.34.192']

LOG_FILE_NAME = 'out.log'
# logging- file handler
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    filename='out.log',
                    filemode='w')

logger = logging.getLogger(__name__)


# creating the console handler
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# console formatter
#formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')

# console handler
logger.addHandler(ch)

# adding rotating file handler
handler = logging.handlers.RotatingFileHandler(
    LOG_FILE_NAME, maxBytes=20000000, backupCount=5)
logger.addHandler(handler)


# reading the environment from command line

mode = os.environ['EnvMode']

with open('config.yml') as config_input:
    config = yaml.load(config_input)

# sqlalchemy_config
engine = create_engine(config[mode]['SQL_ENGINE'], echo=True)

session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

BOOTSTRAP_SERVERS = config[mode]['BOOTSTRAP_SERVERS']
# kafka_config


def consumer_start():
    '''
        This method to get the kafka consumer conneciton
    '''
    try:
        consumer = KafkaConsumer(
            'product_to_scrape', bootstrap_servers=BOOTSTRAP_SERVERS, value_deserializer=lambda v: json.loads(v.decode('utf-8')))
        logger.info(
            'Kafka consumer for the topic "product_to_scrape is created"')
        return consumer
    except Exception as e:
        logger.warn('Kafka Connection issue{0}'.format(e))
        raise RuntimeError


def producer_start():
    '''
    This method is to get kafka producer connection

    '''
    try:
        producer = KafkaProducer(bootstrap_servers=BOOTSTRAP_SERVERS,
                                 value_serializer=lambda v: json.dumps(v).encode('utf-8'))
        logger.info('Kafka producer connection is created')
        return producer
    except Exception as e:
        logger.warn('Kafka Connection issue{0}'.format(e))

        #raise RuntimeError


def transactions(f):

    @wraps(f)
    def wrapper(*args, **kwargs):

        try:
            session = Session()
            result = f(*args, **kwargs)
            session.commit()
            return result
        except (AuthorizationError, AuthenticationError) as e:
            logger.error('An error has occured with the traceback {0}'.format(
                traceback.format_exc()))
            session.rollback()
        except (ValidationError, NotFoundError, MissingFieldError, IllegalAssignmentError, IllegalArgumentError, SparkError) as e:

            logger.error('An error has occured with the traceback {0}'.format(
                traceback.format_exc()))
            session.rollback()
        except BaseError as e:

            logger.error('An error has occured with the traceback {0}'.format(
                traceback.format_exc()))
            session.rollback()
        except Exception as e:
            logger.error('An error has occured with the traceback {0}'.format(
                traceback.format_exc()))
            session.rollback()
        finally:
            Session.remove()

    return wrapper


def timing(func):

    @wraps(func)
    def wrapper(*args, **kwargs):
        t1 = time.time()
        result = func(*args, **kwargs)
        t2 = time.time()
        logger.info('The time taken to serve the request is %s', str(t2-t1))
        return result
    return wrapper
