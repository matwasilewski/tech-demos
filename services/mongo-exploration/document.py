from enum import StrEnum
from beanie import Document as BeanieDocument
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class StudyOutcome(StrEnum):
    """Study outcome"""
    positive = "positive"
    negative = "negative"
    mixed = "mixed"
    neutral = "neutral"

class Document(BeanieDocument):
    """Base document class"""
    created_at: datetime = Field(default_factory=datetime.now)
    title: str
    abstract: str
    authors: List[str]
    

class SystematicReview(Document):
    """Systematic review document"""
    number_of_studies: Optional[int] = None
    primary_outcome: StudyOutcome

class ClinicalTrial(Document):
    """Clinical trial document"""
    number_of_participants: Optional[int] = None
    primary_outcome: StudyOutcome