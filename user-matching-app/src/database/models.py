from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    major = Column(String, nullable=False)
    strengths = Column(Text, nullable=True)
    weaknesses = Column(Text, nullable=True)
    current_classes = Column(Text, nullable=True)

    class_entries = relationship("ClassEntry", back_populates="user")
    portfolio = relationship("Portfolio", uselist=False, back_populates="user")

class ClassEntry(Base):
    __tablename__ = 'class_entries'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    class_name = Column(String, nullable=False)
    grade = Column(String, nullable=True)
    ap_score = Column(Integer, nullable=True)

    user = relationship("User", back_populates="class_entries")

class Portfolio(Base):
    __tablename__ = 'portfolios'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    images = Column(Text, nullable=True)
    markdown_content = Column(Text, nullable=True)

    user = relationship("User", back_populates="portfolio")