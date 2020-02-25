import os
import yaml
import time
import json
import boto3
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

# console handler
logger.addHandler(ch)

# adding rotating file handler
handler = logging.handlers.RotatingFileHandler(
    LOG_FILE_NAME, maxBytes=20000000, backupCount=5)
logger.addHandler(handler)


# reading the enviroment from command line
mode = os.environ['EnvMode']

with open('config.yml') as config_input:
    config = yaml.load(config_input)

# sqlalchemy_config
engine = create_engine(config[mode]['SQL_ENGINE'], echo=True)

session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

BOOTSTRAP_SERVERS = config[mode]['BOOTSTRAP_SERVERS']
# kafka_config

sns_client = boto3.client('sns', aws_access_key_id=config[mode]['AWS_ACCESS_KEY_ID'],
                          aws_secret_access_key=config[mode]['AWS_SECRET_ACCESS_KEY'], region_name=config[mode]['AWS_REGION_NAME'])
ses_client = boto3.client('ses', aws_access_key_id=config[mode]['AWS_ACCESS_KEY_ID'],
                          aws_secret_access_key=config[mode]['AWS_SECRET_ACCESS_KEY'], region_name=config[mode]['AWS_REGION_NAME'])


def consumer_start():
    '''
    This method is to create the kafka connection
    '''
    try:

        consumer = KafkaConsumer(
            'send_sms', 'send_email', 'admin_alert', bootstrap_servers=BOOTSTRAP_SERVERS, value_deserializer=lambda v: json.loads(v.decode('utf-8')))
        logger.info('Kafka consumer connection is created')
        return consumer
    except Exception as e:
        logger.info('There is a kafka conneciton issue')
        raise RuntimeError


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
