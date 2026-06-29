"""
SQLAlchemy ORM models for knowledge extraction pipeline
Maps to desa_punggul MySQL database
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import enum
import os
from dotenv import load_dotenv
from urllib.parse import quote

load_dotenv()

# Database connection
DB_HOST = os.getenv('DB_HOST', '127.0.0.1')
DB_PORT = os.getenv('DB_PORT', '3306')
DB_USER = os.getenv('DB_USERNAME', 'nlp_user')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'NLP@User123')
DB_NAME = os.getenv('DB_DATABASE', 'desa_punggul')

# URL-encode password to handle special characters like @
DB_PASSWORD_ENCODED = quote(DB_PASSWORD, safe='')

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD_ENCODED}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class StatusEnum(str, enum.Enum):
    VALIDATED = "validated"
    PENDING_REVIEW = "pending_review"
    REJECTED = "rejected"


class ValueTypeEnum(str, enum.Enum):
    CONTINUOUS = "continuous"
    CATEGORICAL = "categorical"


class KnowledgeRule(Base):
    """
    Stores extracted IF-THEN rules
    """
    __tablename__ = 'knowledge_rules'

    id = Column(Integer, primary_key=True)
    source_text = Column(Text, nullable=False)
    domain = Column(String(255), nullable=True)
    visibility = Column(String(50), default='private')
    confidence_score = Column(Float, nullable=False)
    extraction_method = Column(String(50), nullable=False)  # 'spacy' or 'llm'
    algorithm_used = Column(String(255), nullable=True)
    condition_group_operator = Column(String(10), nullable=True)  # 'AND' or 'OR'
    action_group_operator = Column(String(10), nullable=True)  # 'AND' or 'OR'
    status = Column(SQLEnum(StatusEnum), default=StatusEnum.PENDING_REVIEW)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    condition_facts = relationship("RuleConditionFact", back_populates="rule", cascade="all, delete-orphan")
    action_facts = relationship("RuleActionFact", back_populates="rule", cascade="all, delete-orphan")


class RuleConditionFact(Base):
    """
    Stores conditions of IF-THEN rules
    """
    __tablename__ = 'rule_condition_facts'

    id = Column(Integer, primary_key=True)
    rule_id = Column(Integer, ForeignKey('knowledge_rules.id'), nullable=False)
    subject = Column(String(255), nullable=False)
    operator = Column(String(20), nullable=False)  # >, <, >=, <=, =, IN, BETWEEN
    logical_operator = Column(String(10), nullable=True)  # 'AND' or 'OR' for next condition
    group_id = Column(Integer, nullable=True)  # For grouping conditions with parentheses
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    rule = relationship("KnowledgeRule", back_populates="condition_facts")
    values = relationship("FactValue", back_populates="condition_fact", 
                         foreign_keys="FactValue.condition_fact_id", cascade="all, delete-orphan")


class RuleActionFact(Base):
    """
    Stores actions of IF-THEN rules
    """
    __tablename__ = 'rule_action_facts'

    id = Column(Integer, primary_key=True)
    rule_id = Column(Integer, ForeignKey('knowledge_rules.id'), nullable=False)
    subject = Column(String(255), nullable=False)
    operator = Column(String(20), nullable=False)  # Usually '='
    logical_operator = Column(String(10), nullable=True)  # 'AND' or 'OR' for next action
    group_id = Column(Integer, nullable=True)  # For grouping actions
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    rule = relationship("KnowledgeRule", back_populates="action_facts")
    values = relationship("FactValue", back_populates="action_fact",
                         foreign_keys="FactValue.action_fact_id", cascade="all, delete-orphan")


class KnowledgeFact(Base):
    """
    Stores extracted subject-relation-object facts
    """
    __tablename__ = 'knowledge_facts'

    id = Column(Integer, primary_key=True)
    source_text = Column(Text, nullable=False)
    subject = Column(String(255), nullable=False)
    relation = Column(String(255), nullable=False)
    domain = Column(String(255), nullable=True)
    visibility = Column(String(50), default='private')
    confidence_score = Column(Float, nullable=False)
    extraction_method = Column(String(50), nullable=False)  # 'spacy' or 'llm'
    algorithm_used = Column(String(255), nullable=True)
    status = Column(SQLEnum(StatusEnum), default=StatusEnum.PENDING_REVIEW)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    values = relationship("FactValue", back_populates="fact",
                         foreign_keys="FactValue.fact_id", cascade="all, delete-orphan")


class FactValue(Base):
    """
    Stores values for rules and facts
    Each rule/fact can have multiple values
    """
    __tablename__ = 'fact_values'

    id = Column(Integer, primary_key=True)
    fact_id = Column(Integer, ForeignKey('knowledge_facts.id'), nullable=True)
    condition_fact_id = Column(Integer, ForeignKey('rule_condition_facts.id'), nullable=True)
    action_fact_id = Column(Integer, ForeignKey('rule_action_facts.id'), nullable=True)
    value_type = Column(SQLEnum(ValueTypeEnum), nullable=False)
    value_continuous = Column(Float, nullable=True)
    value_categorical = Column(String(255), nullable=True)
    unit = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    fact = relationship("KnowledgeFact", back_populates="values")
    condition_fact = relationship("RuleConditionFact", back_populates="values")
    action_fact = relationship("RuleActionFact", back_populates="values")


def get_session():
    """Get a database session"""
    return SessionLocal()


def init_db():
    """Initialize database tables"""
    try:
        Base.metadata.create_all(engine)
        print(" Database tables created successfully")
    except Exception as e:
        print(f" Error creating database tables: {str(e)}")