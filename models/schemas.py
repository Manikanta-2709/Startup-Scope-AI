from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class StartupIdea(BaseModel):
    idea_name: str
    description: str
    target_users: str

class Competitor(BaseModel):
    name: str
    description: str

class AnalysisResult(BaseModel):
    competitors: List[Competitor]
    strengths: List[str]
    weaknesses: List[str]
    market_gaps: List[str]
    improvements: List[str]
    idea_score: float
    confidence: str
    justification: str

class IdeaRecord(BaseModel):
    idea_name: str
    description: str
    target_users: str
    analysis: AnalysisResult
    created_at: datetime = datetime.now()
