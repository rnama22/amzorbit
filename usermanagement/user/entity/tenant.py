'''Account obj '''

from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, BOOLEAN, TIMESTAMP, ForeignKey

Base = declarative_base()

# Check how sqlalchemy supports validation!


class Tenant(Base):
    __tablename__ = 'tenant'

    tenant_id = Column(Integer, primary_key=True)
    tenant_name = Column(String)
    create_dt = Column(TIMESTAMP)
    update_dt = Column(TIMESTAMP)
    created_by = Column(Integer)
    updated_by = Column(Integer)
    settings = Column(String)
