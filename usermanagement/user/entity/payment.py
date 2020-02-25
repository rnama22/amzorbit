import yaml

from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, BOOLEAN, TIMESTAMP, ForeignKey

Base = declarative_base()

# Check how sqlalchemy supports validation!


class Payment(Base):
    __tablename__ = 'payment'

    id = Column(Integer, primary_key=True)
    last4 = Column(String)
    brand = Column(String)
    exp_month = Column(String)
    exp_year = Column(String)
    name = Column(String)
    stripe_token = Column(String)
    user_id = Column(Integer)    
    create_dt = Column(TIMESTAMP)
    update_dt = Column(TIMESTAMP)
    created_by = Column(Integer)
    updated_by = Column(Integer)

