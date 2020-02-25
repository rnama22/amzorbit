from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey

Base = declarative_base()


class Alert(Base):
    __tablename__ = 'alert'

    id = Column(Integer, primary_key=True)
    alert_type = Column(String)
    message = Column(String)
    meta_data = Column(String)
    status = Column(String)
    create_dt = Column(TIMESTAMP)
    update_dt = Column(TIMESTAMP)
    created_by = Column(Integer)
    updated_by = Column(Integer)
    product_id = Column(Integer)
    tenant_id = Column(Integer)
