from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Workflow(Base):
    __tablename__ = 'workflows'

    id = Column(Integer, primary_key=True)
    name = Column(String(length=100))

    nodes = relationship("Node", back_populates="workflow")


class Node(Base):
    __tablename__ = 'nodes'

    id = Column(Integer, primary_key=True)
    type = Column(String(length=50))
    status = Column(String(length=50))
    message_text = Column(String(length=100))
    outgoing_edge = Column(String(length=50))
    yes_edge = Column(String(length=50))
    no_edge = Column(String(length=50))
    workflow_id = Column(Integer, ForeignKey('workflows.id'))

    workflow = relationship("Workflow", back_populates="nodes")

  