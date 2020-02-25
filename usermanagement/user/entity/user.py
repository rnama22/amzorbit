import yaml
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, BOOLEAN, TIMESTAMP, ForeignKey

Base = declarative_base()

# Check how sqlalchemy supports validation!

# var
TRANSIENT_ATTR = ['expiry']


def user_from_dict(user_attributes):
    '''
    Delets the transient variable
    '''

    for key in TRANSIENT_ATTR:
        user_attributes.pop(key, None)
    return User(**user_attributes)


class User(Base):

    __tablename__ = 'user'

    user_id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    email_id = Column(String)
    mobile_num = Column(Integer)
    create_dt = Column(TIMESTAMP)
    update_dt = Column(TIMESTAMP)
    created_by = Column(Integer)
    updated_by = Column(Integer)
    tenant_id = Column(Integer)
    email_alert = Column(BOOLEAN)
    sms_alert = Column(BOOLEAN)
    email_daily_digest = Column(BOOLEAN)
    alert_preference = Column(String)
    email_validation = Column(BOOLEAN)
    subscription_id = Column(Integer)
    suscription_expiry = Column(TIMESTAMP)

    @hybrid_property
    def expiry(self):
        print('hybrid property debug one')
        se = self.suscription_expiry
        ct = datetime.utcnow()
        if se is None or ((ct - se).days < 0):
            return False
        else:
            return True
