from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

class SlangEntry(BaseModel):
    model_config = ConfigDict(
        frozen=True,  # Immutable for safety
        extra="forbid"
    )

    term: str
    definition: str
    era: str = Field(..., description="Format: YYYYQn, e.g., '2023Q4'")
    region: str
    platform: str
    vibe_tags: List[str]
    popularity_score: int = Field(..., ge=0, le=100)
    audio_reference: Optional[str] = None
    is_offensive: bool = False
    related_terms: List[str] = Field(default_factory=list)

class SlangFilter(BaseModel):
    """Used for advanced filtering in SlangDB.search()"""
    term_contains: Optional[str] = None
    min_popularity: int = 0
    max_popularity: int = 100
    regions: Optional[List[str]] = None
    platforms: Optional[List[str]] = None
    vibe_tags: Optional[List[str]] = None
    era_start: Optional[str] = None  # "2023Q1"
    era_end: Optional[str] = None
    exclude_offensive: bool = False
