import json

from flask import request
from flask_restful import Resource

from process.globalutils import timing, transactions, logger
from process.service.ipservice import IPService


class IPAddController(Resource):

    ''' 
    This method is to controll the user login 
    '''

    ip_service = IPService()

    @timing
    @transactions
    def post(self):

        ip_payload = request.get_json(force=True)
        logger.info('Post method is called to add the IP')

        if ip_payload['secret_key'] == 'icanprotect':
            self.ip_service.add(ip_payload['ip'])
