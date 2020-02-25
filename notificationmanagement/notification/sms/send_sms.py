import boto3
import json

from notification.globalutils import sns_client, logger


class Send_Sms:

    def sms_send(self, alert_info):
        '''
        This method is to send alerts using mobile
        '''

        mobile_numbers = json.loads(alert_info['mobile_num'])

        for number in mobile_numbers:
            number = '+1' + str(number)

            logger.info(
                'An alert is being sent for the mobile number {0}'.format(number))

            if 'asin' in alert_info:
                amazon_link = 'https://www.amazon.com/dp/{0}'.format(
                    alert_info['asin'])

                amazon_orbit_link = 'https://app.amzorbit.com/#/product/{0}'.format(
                    alert_info['product_id'])

                links = "                  [View On AmzOrbit: {0}]      [View On Amazon: {1}]".format(
                    amazon_orbit_link, amazon_link)

                attributes = ', '.join(json.loads(
                    alert_info['diffAttributes']))

                message = alert_info['message'] + ":" + \
                    ' {0}'.format(attributes)

                message = "Amzorbit Alert for {0}: {1}  {2} {3} ".format(
                    alert_info['asin'], message,  (alert_info['title'][:20])+'..', links)
            else:
                message = alert_info['message']

            response = sns_client.publish(
                PhoneNumber=number, Message=message)

            logger.info('An alert is sent using sns client with the response {0}'.format(
                json.dumps(response)))
