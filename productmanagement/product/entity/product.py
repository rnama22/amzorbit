import yaml

from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, BOOLEAN, TIMESTAMP, ForeignKey


Base = declarative_base()

# Check how sqlalchemy supports validation!


class Product(Base):
    __tablename__ = 'product'

    id = Column(Integer, primary_key=True)
    uid = Column(String)
    asin = Column(String)
    platform = Column(String)
    ideal_state = Column(String)
    health_status = Column(String)
    title = Column(String)
    product_info_status = Column(String)
    market = Column(String)
    current_state = Column(String)
    state_diff = Column(String)
    image = Column(String)
    create_dt = Column(TIMESTAMP)
    update_dt = Column(TIMESTAMP)
    created_by = Column(Integer)
    updated_by = Column(Integer)
    tenant_id = Column(Integer)
    archive = Column(BOOLEAN)
    refresh_dt = Column(TIMESTAMP)
