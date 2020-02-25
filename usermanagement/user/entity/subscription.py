import yaml

from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, BOOLEAN, TIMESTAMP, ForeignKey

Base = declarative_base()

# Check how sqlalchemy supports validation!


class Subscription(Base):
    __tablename__ = 'subscription'

    id = Column(Integer, primary_key=True)
    plan_id = Column(String)
    plan_name = Column(String)
    # tenant_id = Column(Integer)
    create_dt = Column(TIMESTAMP)
    update_dt = Column(TIMESTAMP)
    created_by = Column(Integer)
    updated_by = Column(Integer)
