''' Service layer for user controller '''
import json
import yaml
import uuid
import bcrypt
import boto3
import requests
import pystache

from datetime import datetime, timedelta
from botocore.exceptions import ClientError
from flask_jwt_extended import create_access_token, create_refresh_token, decode_token

from globalinfo.globalutils import Session, ses_client, mode, logger
from usermanagement.user.entity.user import User, user_from_dict
from usermanagement.user.entity.tenant import Tenant
from usermanagement.user.entity.account import Account


with open('config.yml') as config_input:
    config = yaml.load(config_input)


MAILGUN_API_KEY = config[mode]['MAILGUN_API_KEY']
MAILGUN_DOMAIN_NAME = config[mode]['MAILGUN_DOMAIN_NAME']
APP_IP = config[mode]['APP_IP']


class UserService:
    ''' This class handles all the methods for use entity'''

    validate_email_api = '/?#/pages/validate-email-page'
    validate_eamil_subject = "AMZOrbit: E-mail Validate"

    def payload_create(self, payload):
        '''
            Generating payload for creating tenant, user, and account
        '''

        user_payload = {}
        account_payload = {}
        tenant_payload = {}

        if 'mobile_num' not in payload:
            payload['mobile_num'] = None

        if 'tenant_name' not in payload:
            payload['tenant_name'] = None

        if 'alert_preference' in payload:
            payload['alert_preference'] = json.dumps(
                payload['alert_preference'])
        else:
            payload['alert_preference'] = []

        if 'email_alert' not in payload:
            payload['email_alert'] = True
        if 'sms_alert' not in payload:
            payload['sms_alert'] = True

        if 'first_name' in payload and 'last_name' in payload:
            user_payload = {'first_name': payload['first_name'], 'last_name': payload['last_name'],
                            'email_id': payload['email_id'], 'mobile_num': payload['mobile_num'], 'alert_preference': payload['alert_preference'], 'email_alert': payload['email_alert'], 'sms_alert': payload['sms_alert'], 'email_validation': False, 'email_daily_digest': True, 'suscription_expiry': datetime.utcnow() + timedelta(days=7)}

        if 'user_name' in payload and 'password' in payload:
            account_payload = {
                'user_name': payload['user_name'], 'password': payload['password']}

        if 'tenant_name' in payload and payload['tenant_name']:
            tenant_payload = {'tenant_name': payload['tenant_name']}
        else:
            tenant_payload = {'tenant_name': None}

        return (user_payload, account_payload, tenant_payload)

    def register(self, payload):
        '''
            This method is for the user registration.

            Checks if the account with the given name exists.

            If not, tenant, account, and user entry will be created

        '''

        logger.info('User registration is in progress for the prospective user with the given user name {0}'.format(
            payload['user_name']))
        # verify if any account with the given user name exist
        acc_exists = self.account_verify(payload['user_name'])

        user_payload, account_payload, tenant_payload = self.payload_create(
            payload)

        logger.info('payload is being created for the user')

        if not acc_exists:

            user_payload, account_payload, tenant_payload = self.payload_create(
                payload)

            logger.info('payload is being created for the user')

            # creating tenant
            tenant_id = self.tenant_create(
                tenant_payload['tenant_name'])

            # creating user
            user_payload['tenant_id'] = tenant_id
            user_new = self.user_create(user_payload)
            account_payload['user_id'] = user_new.user_id
            account_payload['tenant_id'] = user_new.tenant_id

            # creating account
            self.account_create(account_payload)

            info = 'Hello, <br/> Welcome to AmzOrbit! We are happy you are here. <br/><br/> First things first, <br/> Let us get started by clicking this link:'
            tag = 'Validate Your E-mail'

            # to validate email
            self.send_jwt_token(
                user_new, self.validate_email_api, self.validate_eamil_subject, info, tag)
        else:
            # externalize all these messages
            logger.info('An account with the user name {0} already exists'.format(
                payload['user_name']))
            return ('error', 'Hey, An account with this user name already exists', None)

        return ('success', 'User Registration is Successful', None)

    def account_verify(self, user_name):
        '''
            This is to retrieve the account object

            #replace it to return true/false based on the account exisiting
        '''

        session = Session()
        account = session.query(Account).filter(
            Account.user_name == user_name).one_or_none()

        if account == None:
            return False
        else:
            return True

    def tenant_create(self, tenant_name):
        '''
            This method is to create the tenant.

            Tenant name can be null
        '''

        session = Session()

        default_info = {'create_dt': datetime.utcnow(),
                        'update_dt': datetime.utcnow()}

        tenant_obj_info = {**{'tenant_name': tenant_name}, **default_info}
        tenant = Tenant(**tenant_obj_info)
        session.add(tenant)
        session.commit()
        logger.info(
            'Tenant is created with the id {0}'.format(tenant.tenant_id))
        return tenant.tenant_id

    def account_create(self, account_payload):
        '''
            This method is to create the account for the user

            User name and password are manadatory
        '''

        logger.info('an account is being created with the user name {0}'.format(
            account_payload['user_name']))
        session = Session()

        account_exists = self.account_verify(account_payload['user_name'])

        default_info = {'create_dt': datetime.utcnow(),
                        'update_dt': datetime.utcnow()}

        hashed_pwd = bcrypt.hashpw(
            account_payload['password'].encode('utf-8'), bcrypt.gensalt(12))

        account_info = {'user_name': account_payload['user_name'], 'password': hashed_pwd,
                        'user_id': account_payload['user_id'], 'tenant_id': account_payload['tenant_id']}
        account_obj_info = {**account_info, **default_info}
        account_obj = Account(**account_obj_info)

        if not account_exists:
            session.add(account_obj)
            session.commit()
            logger.info('An account is created for the user {0}'.format(
                account_obj.user_name))
        else:
            logger.info('An account already exists with the user name {0}'.format(
                account_info['user_name']))
            return ('error', 'An Account already exists for the user', None)

        return ('success', 'Account successfully created', None)

    def user_create(self, user_payload):
        '''
        A method to create an user
        '''

        session = Session()

        default_info = {'create_dt': datetime.utcnow(),
                        'update_dt': datetime.utcnow()}

        logger.info('User registration is in progress')
        user_obj = {**user_payload, **default_info}
        user = User(**user_obj)
        session.add(user)
        session.commit()

        return user

    def invite_user(self, payload, user_id, tenant_id):
        '''
            This method is to add another user for the tenant
        '''

        user_payload, account_payload, tenant_payload = self.payload_create(
            payload)

        user_payload['created_by'] = user_id
        user_payload['tenant_id'] = tenant_id
        user_payload['email_validation'] = True
        user = self.user_create(user_payload)

        api = '/api/user/accountcreate'
        subject = 'AMZOrbit: New User Registration'
        # edit the info
        info = 'Hello, <br/> Welcome to AmzOrbit! We are happy you are here. <br/><br/> First things first, <br/> Let us get started by clicking this link:'
        tag = 'Validate Your E-mail'

        self.send_jwt_token(user, api, subject, info, tag)

        return ('success', 'An e-mail is sent to User for Registration', user)

    def user_account_create(self, payload):
        '''
        This method  is to create a new account when the user payload is given
        '''

        user_payload, account_payload, tenant_payload = self.payload_create(
            payload)
        account_payload['user_id'] = payload['user_id']
        account_payload['tenant_id'] = payload['tenant_id']

        account = self.account_create(account_payload)

        # user email_verification update
        if account[0] == 'error':
            return ('error', 'Hey, An account with this user name already exists', None)

        return ('success', 'Account successfully created', None)

    def get(self, user_id, tenant_id):
        '''
            This method retrieves the user info
        '''
        session = Session()
        user = session.query(User).filter(
            User.user_id == user_id).filter(
            User.tenant_id == tenant_id).one_or_none()

        if user is None:
            logger.error('User with user_id {0} and tenant_id {1} doesnot exist'.format(
                user_id, tenant_id))
            return ('error', 'User doesnt exist', None)

        logger.info('User info is retreived for the user_id {0} and tenant_id {1} with the user info {2}'.format(
            user_id, tenant_id, user.email_id))

        return ('success', 'User Info Retrieved', user)

    def update(self, user_payload):
        '''
            This method is to update the user info
        '''

        session = Session()

        user_payload['update_dt'] = datetime.utcnow()

        # calling method to remove transient variables
        user = user_from_dict(user_payload)

        if 'alert_preference' in user_payload:
            user_payload['alert_preference'] = json.dumps(
                user_payload['alert_preference'])

        session.query(User).filter(
            User.user_id == user.user_id).filter(
            User.tenant_id == user.tenant_id).update(user_payload)
        session.commit()

        updated_user = self.get(user.user_id, user.tenant_id)

        if updated_user[0] == 'error':

            logger.error('User info cant be updated as user with user_id {0} and tenant_id {1} doesnot exist '.format(
                user_payload['user_id'], user_payload['tenant_id']))
            return ('error', 'User doesnt exist', None)
        return ('success', 'User Info Updated Sucessfully', updated_user[2])

    def delete(self, user_id):
        '''Deletes User Info'''

        return 'working on it'

    def authenticate_user(self, account_payload):
        '''
            This method is to authenticate the user

            Takes the username and password.

            Validates the password with the existing password using bcrypt.

            Jwt token is sent in response upon succesful authentication
        '''

        session = Session()

        user_name = account_payload['user_name']
        password = account_payload['password']

        acc_user = session.query(Account).filter(
            Account.user_name == user_name).one_or_none()

        session.commit()
        if acc_user:
            if bcrypt.checkpw(
                    password.encode('utf-8'), acc_user.password.encode('utf-8')):
                jwt_token = self.jwt_generate(acc_user)
                logger.info(
                    'User info is validated the authentication is successful for the user {0}'.format(user_name))
                return ('success', 'User Authentication Is Successful', jwt_token)

        else:
            logger.info(
                'User info couldnot be validated for the user name {0}'.format(user_name))
            return ('error', 'Either User Name or Password is Incorrect', None)

    def password_update(self, account_payload):
        '''
            This method is to update the password

            Needs to test yet
        '''

        session = Session()

        user_id = account_payload['user_id']
        acc_user = session.query(Account).filter(
            Account.user_id == user_id).one_or_none()

        if bcrypt.checkpw(account_payload['old_password'].encode('utf-8'), acc_user.password.encode('utf-8')):
            updated_pwd = bcrypt.hashpw(
                account_payload['new_password'].encode('utf-8'), bcrypt.gensalt(12))

            default_info = {'create_dt': datetime.utcnow(),
                            'update_dt': datetime.utcnow()}

            account_info = {'user_id': user_id, 'password': updated_pwd}
            account_obj_info = {**account_info, **default_info}
            session.query(Account).filter(
                Account.user_id == user_id).update(account_obj_info)
            session.commit()
            logger.info(
                'Password is sucessfully updated for the user with id {0}'.format(user_id))
            return ('success', 'Password Successfully Updated', None)
        else:
            return ('error', 'Password Entered is Incorrect', None)

    def tenant_update(self, tenant_id, tenant_payload):
        '''
            This method is to update the tenant
        '''

        session = Session()

        logger.info('The tenant with the id {0} is being updated with the info {1} '.format(
            tenant_id, json.dumps(tenant_payload)))

        tenant_payload['update_dt'] = datetime.utcnow()
        if 'settings' in tenant_payload:
            tenant_payload['settings'] = json.dumps(tenant_payload['settings'])

        tenant = session.query(Tenant).filter(Tenant.tenant_id ==
                                              tenant_id).update(tenant_payload)
        session.commit()

        tenant = self.tenant_get(tenant_id)
        return('success', 'Tenant Info Updated Successfully', tenant[2])

    def users_list_tenant(self, tenant_id):
        '''
        Pulls the user list for a tenant
        '''
        session = Session()
        users = session.query(User).filter(
            User.tenant_id == tenant_id).all()
        if users:
            return ('success', 'users info is retrieved for the tenant', users)
        else:
            return ('error', 'No users exists for the given tenant', None)

    def tenants_all(self):
        '''
        Returns all tenant-- required for product service module
        '''
        session = Session()
        tenants = session.query(Tenant).all()
        logger.info('Retrived all the tenants info')
        return tenants

    def tenant_get(self, tenant_id):
        '''
            This method is to retrieve the tenant info
        '''
        session = Session()

        tenant = session.query(Tenant).filter(Tenant.tenant_id ==
                                              tenant_id).one_or_none()
        session.commit()

        if tenant is None:
            logger.error(
                'Tenant with the id {0} couldnt be found'.format(tenant_id))
            return('error', 'Tenant could not be found', None)
        else:

            logger.info(
                'Tenant info sucessfully retrived for the tenant {0}'.format(tenant_id))

            return('success', 'Tenant Info Retrieved Successfully', tenant)

    def jwt_generate(self, user):
        '''
            This method is to generate jwt token
        '''
        logger.info('Jwt token is being generated')
        token = {'access_token': create_access_token(identity=user)}
        return token
    # check this!

    # needs work
    def jwt_token_refresh(self, user_id):
        '''
         In progress
        '''

        session = Session()
        acc_user = session.query(Account).filter(
            Account.user_name == user_id).one_or_none()
        jwt_token = self.jwt_generate(acc_user)
        session.commit()
        return jwt_token

    def jwt_token_decode(self, token):
        '''
            Decoding the token to get data stored in it
        '''
        data = decode_token(token)
        return data

    def users_email_info(self, tenant_id):
        '''
        Sends email list for users related to tenant- required for product service module
        '''

        email_list = []
        session = Session()

        users = session.query(User).filter(User.tenant_id == tenant_id).filter(User.email_validation == True).filter(
            User.email_daily_digest == True).all()

        if users:
            for user in users:
                if user.email_id and user.email_id not in email_list:
                    email_list.append(user.email_id)
            logger.info(
                'Email list of all the users is composed for the tenant {0}'.format(tenant_id))
        return email_list

    def user_email_validate(self, token):
        '''
         This method is to validate the email
        '''
        session = Session()

        # calling method to decode the token
        data = self.jwt_token_decode(token)

        # Extracting the user_id and tenant_id from the decoded data of the payload
        user_id = data['identity']
        tenant_id = data['user_claims']['tenant_id']

        user = session.query(User).filter(
            User.user_id == user_id).filter(
            User.tenant_id == tenant_id).one_or_none()

        if user is None:
            return ('error', 'Unable to verify the account, please request again', None)
        else:

            user.email_validation = True
            session.add(user)
            session.commit()

            return('success', 'E-mail is successfully validated', None)

    def validate_email_resend(self, user_id, tenant_id):
        '''
            Pulls the user info and re-sends an email to validate
        '''
        info = 'Hello, <br/> Welcome to AmzOrbit! We are happy you are here. <br/><br/> First things first, <br/> Let us get started by clicking this link:'
        tag = 'Validate Your E-mail'
        session = Session()

        user = session.query(User).filter(
            User.tenant_id == tenant_id).filter(
            User.user_id == user_id).one_or_none()

        if user:
            self.send_jwt_token(
                user, self.validate_email_api, self.validate_eamil_subject, info, tag)

            return ('success', 'Validation email is successfully sent', None)
        else:
            return ('error', 'An account with the user info doesnot exist', None)

    def send_jwt_token(self, user, api, subject, info, tag_name):
        '''
            send_jwt_token
        '''
        logger.info('Progressing the process of sending jwt token')
        jwt_token = self.jwt_generate(user)
        user_id = user.user_id
        token = jwt_token['access_token']
        session = Session()
        default_info = {'create_dt': datetime.utcnow(),
                        'update_dt': datetime.utcnow()}

        account_info = {'user_id': user_id, 'jwt_token': token}
        account_obj_info = {**account_info, **default_info}
        session.query(Account).filter(
            Account.user_id == user_id).update(account_obj_info)

        session.commit()

        link = '{0}{1}?digest={2}'.format(
            APP_IP, api, jwt_token['access_token'])

        # formating the e-mail
        email_context = self.email_formatting(
            subject, user.email_id, link, info, tag_name)

        # sending the e-mail
        self.send_email(email_context)

    def email_formatting(self, subject, email_id, link, info, tag_name):
        '''
        Formating the email
        '''

        logger.info('formatting e-mail')
        email_context = {}
        email_context['text'] = (link)
        context = {
            'subject': subject,
            'info': info,
            'link': link,
            'tag_name': tag_name
        }
        # The subject line for the email.
        # info = 'Hello, <br/> Welcome to AmzOrbit! We are happy you are here. <br/><br/> First things first, <br/> Let us get started by clicking this link:'

        email_context['html'] = pystache.render("""<html>
        <head></head
        <body>
            <h1>{{subject}}</h1>
            <p>{{info}}</p>
            <a href='{{link}}'>{{tag_name}}</a>
        </body>
        </html>""", context)

        email_context['subject'] = subject
        email_context['to'] = email_id
        return email_context

    def send_email(self, email_context):
        '''
        This method is to send emails for inviting users

        '''

        logger.info('sending email to the user with email_id {0}'.format(
            email_context['to']))
        url = 'https://api.mailgun.net/v3/{0}/messages'.format(
            MAILGUN_DOMAIN_NAME)

        auth = ('api', MAILGUN_API_KEY)
        data = {
            'from': 'AMZ Orbit <alert@amzorbit.com>',
            'to': email_context['to'],
            'subject': email_context['subject'],
            'text': email_context['text'],
            'html': email_context['html']
        }
        response = requests.post(url, auth=auth, data=data)
        response.raise_for_status()

    def resetpasswordlink(self, user_payload):
        '''
            This method is to reset the password of the user

            Takes the username

            Email is sent in response upon succesful authentication
        '''

        update_email_api = '/?#/pages/update-password-page'
        reset_email_subject = "AMZOrbit: Reset password"

        session = Session()

        user_name = user_payload['user_name']

        acc_user = session.query(Account).filter(
            Account.user_name == user_name).one_or_none()
        if acc_user:
            user_id = acc_user.user_id

            user = session.query(User).filter(
                User.user_id == user_id).one_or_none()

            session.commit()

            if user:
                info = 'Hello, <br/> Please follow the below link to reset your password. <br/> <br/>'
                tag_name = 'Reset Your Password'
                self.send_jwt_token(
                    user, update_email_api, reset_email_subject, info, tag_name)

                return ('success', 'An Email is successfully sent', None)
        else:
            return ('error', 'Couldnot find an accout with the provided user name. Please enter a valid user name', None)

    def password_reset(self, user_payload):
        '''
            This method is to reset the password of the user

            Takes the username and tokenn

        '''

        session = Session()
        token = user_payload['token']
        validation = self.validate_jwt_token(token)
        if (validation[0] == 'success'):
            jwt_token = None
            token = token['digest']
            data = self.jwt_token_decode(token)
            user_id = data['identity']
            tenant_id = data['user_claims']['tenant_id']
            updated_pwd = bcrypt.hashpw(
                user_payload['new_password'].encode('utf-8'), bcrypt.gensalt(12))

            default_info = {'create_dt': datetime.utcnow(),
                            'update_dt': datetime.utcnow()}
            # make the jwt token invalid
            account_info = {'user_id': user_id,
                            'password': updated_pwd, 'jwt_token': jwt_token}
            account_obj_info = {**account_info, **default_info}
            session.query(Account).filter(
                Account.user_id == user_id).filter(
                Account.tenant_id == tenant_id).update(account_obj_info)

            session.commit()
            logger.info(
                'Password is sucessfully updated for the user with id {0}'.format(user_id))
            return ('success', 'Password reset is Successful', None)
        else:
            return('error', ' The linked is not valided. Please request for a new reset link again', None)

    def validate_jwt_token(self, payload):
        '''
            This method is to validate jwt token

            Takes the token 

        '''
        session = Session()
        token = payload['digest']
        data = self.jwt_token_decode(token)
        # Extracting the user_id and tenant_id from the decoded data of the payload
        user_id = data['identity']
        tenant_id = data['user_claims']['tenant_id']

        acc_user = session.query(Account).filter(
            Account.user_id == user_id).filter(
            Account.tenant_id == tenant_id).one_or_none()

        if (acc_user.jwt_token == token):
            return ('success', 'Token is valid', None)
        else:
            return('error', 'The linked is not valided. Please request for a new reset link again', None)
