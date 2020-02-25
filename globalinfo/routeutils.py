""" class to handle errors and send results """
import traceback
import json

from datetime import datetime
from bson import json_util
from functools import wraps
from sqlalchemy.ext.declarative import DeclarativeMeta

from globalinfo.globalutils import logger
from .exceptions import *


class HTTPStatusCode:
    """ Class having HTTP response status codes"""
    OK = 200
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    INTERNAL_SERVER_ERROR = 500


class AlchemyEncoder(json.JSONEncoder):
    def default(self, obj):
        print('In the encoder func {0}'.format(obj))
        logger.error('In the encoder func {0}'.format(obj))
        if isinstance(obj.__class__, DeclarativeMeta):
            # an SQLAlchemy class
            fields = {}
            for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:

                print('In the for loop of encoder {0}'.format(field))
                data = obj.__getattribute__(field)
                try:
                    if isinstance(data, datetime):
                        print(
                            'Converting to dict from object in encoder {0}'.format(data))
                        data = str(data)
                    fields[field] = data
                except TypeError:
                    logger.info('Failed in encoder exception {0}'.format(
                        fields[field]))
                    fields[field] = None
            return fields
        return json.JSONEncoder.default(self, obj)


def error_handler(f):
    @wraps(f)
    def wrapper(*args, **kwargs):

        try:
            return f(*args, **kwargs)
        except (AuthorizationError, AuthenticationError) as e:
            print(e)
            logging.error(traceback.format_exc(e))
            result = {'status': 'error', 'message': e.message, 'data': ''}
            return result
        except (ValidationError, NotFoundError, MissingFieldError, IllegalAssignmentError, IllegalArgumentError, SparkError) as e:
            print(e)
            logging.error(traceback.format_exc(e))
            result = {'status': 'error', 'message': e.message, 'data': ''}
            return result
        except BaseError as e:
            print(e)
            logging.error(traceback.format_exc(e))
            result = {'status': 'error', 'message': e.message, 'data': ''}
            return result
        except Exception as e:
            print(e)
            logging.error(traceback.format_exc(e))
            result = {'status': 'error', 'message': e.args[0], 'data': ''}
            return result
    return wrapper


def results(status='success', message='', data=[], format_json=True):

    print('Before the encder in results')
    logger.info('Before the encoder in results {0}'.format(data))
    output_data = json.loads(AlchemyEncoder().encode(data))
    output = {'status': status, 'message': message, 'data': output_data}
    logger.info('The encoded result is {0}'.format(output))
    return output
