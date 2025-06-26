from datetime import datetime, timezone
from typing import Dict, Any
import uuid

from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, JSON, Text, UniqueConstraint
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

Base = declarative_base()


class Company(Base):
    """SQLAlchemy model for Company table, matching Prisma schema."""
    __tablename__ = "Company"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    ticker = Column(String, unique=True, nullable=False)
    sector = Column(String, nullable=True)
    industry = Column(String, nullable=True)
    createdAt = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updatedAt = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    financial_data = relationship("FinancialData", back_populates="company")
    analysis_results = relationship("AnalysisResult", back_populates="company")


class FinancialData(Base):
    """SQLAlchemy model for FinancialData table, matching Prisma schema."""
    __tablename__ = "FinancialData"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    companyId = Column(String, ForeignKey("Company.id"), nullable=False)
    year = Column(Integer, nullable=False)
    period = Column(String, nullable=False)  # e.g., "Q1", "Q2", "FY"
    data = Column(JSON, nullable=False)  # JSONB field for raw financial statements
    createdAt = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updatedAt = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    company = relationship("Company", back_populates="financial_data")
    
    # Unique constraint to match Prisma schema
    __table_args__ = (
        UniqueConstraint('companyId', 'year', 'period', name='_companyId_year_period_unique'),
    )


class AnalysisTemplate(Base):
    """SQLAlchemy model for AnalysisTemplate table, matching Prisma schema."""
    __tablename__ = "AnalysisTemplate"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    sectors = Column(JSON, nullable=False)  # Array of strings
    template = Column(JSON, nullable=False)  # The prompt chain and scoring logic
    createdAt = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updatedAt = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    results = relationship("AnalysisResult", back_populates="template")


class AnalysisResult(Base):
    """SQLAlchemy model for AnalysisResult table, matching Prisma schema."""
    __tablename__ = "AnalysisResult"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    companyId = Column(String, ForeignKey("Company.id"), nullable=False)
    templateId = Column(String, ForeignKey("AnalysisTemplate.id"), nullable=False)
    jobId = Column(String, ForeignKey("BulkAnalysisJob.id"), nullable=True)
    score = Column(Float, nullable=False)
    insights = Column(JSON, nullable=False)  # LLM-generated insights
    metricScores = Column(JSON, nullable=False)  # Detailed breakdown of scores
    createdAt = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updatedAt = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    company = relationship("Company", back_populates="analysis_results")
    template = relationship("AnalysisTemplate", back_populates="results")
    job = relationship("BulkAnalysisJob", back_populates="results")


class BulkAnalysisJob(Base):
    """SQLAlchemy model for BulkAnalysisJob table, matching Prisma schema."""
    __tablename__ = "BulkAnalysisJob"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    status = Column(String, nullable=False)  # e.g., "PENDING", "IN_PROGRESS", "COMPLETED", "FAILED"
    progress = Column(Float, default=0.0, nullable=False)
    createdAt = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updatedAt = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    results = relationship("AnalysisResult", back_populates="job") 