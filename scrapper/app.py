import os
import yaml

from flask import Flask
from flask_cors import CORS
from flask_restful import Resource, Api
from flask_jwt_extended import JWTManager

from process.globalutils import logger
from process.que.kafkaconsumerspyder import KafkaConsumerSpyder


APP = Flask(__name__)
CORS(APP)
API = Api(APP)


skp = KafkaConsumerSpyder()
skp.kafka_consumer_start()


with open('config.yml') as config_input:
    config = yaml.load(config_input)

# Or can import mode from global utils
mode = os.environ['EnvMode']
if __name__ == '__main__':
    logger.info('app is launched')
    APP.run(host=config[mode]['APP_HOST'],
            port=config[mode]['APP_PORT'], debug=True,  threaded=True)
