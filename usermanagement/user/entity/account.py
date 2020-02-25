'''Account obj '''

from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, BOOLEAN, TIMESTAMP, ForeignKey

Base = declarative_base()

# Check how sqlalchemy supports validation!


class Account(Base):
    __tablename__ = 'account'

    account_id = Column(Integer, primary_key=True)
    user_name = Column(String)
    password = Column(String)
    create_dt = Column(TIMESTAMP)
    update_dt = Column(TIMESTAMP)
    created_by = Column(Integer)
    updated_by = Column(Integer)
    tenant_id = Column(Integer)
    user_id = Column(Integer)
    jwt_token = Column(String)
