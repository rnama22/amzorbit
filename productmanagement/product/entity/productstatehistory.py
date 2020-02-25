from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey

Base = declarative_base()


class ProductStateHistory(Base):
    __tablename__ = 'product_state_history'

    id = Column(Integer, primary_key=True)
    current_state = Column(String)
    state_diff = Column(String)
    ideal_state = Column(String)
    create_dt = Column(TIMESTAMP)
    update_dt = Column(TIMESTAMP)
    created_by = Column(Integer)
    product_id = Column(Integer)
    tenant_id = Column(Integer)
