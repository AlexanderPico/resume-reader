from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class Personal(BaseModel):
    full_name: Optional[str] = Field(None, description="Full legal name")
    email: Optional[str] = Field(None, description="Primary email address")
    phone: Optional[str] = Field(None, description="Phone number in international format")
    location: Optional[str] = Field(None, description="Current location / city, country")


class ExperienceItem(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    start: Optional[str] = Field(None, description="ISO date or year e.g. 2020-05")
    end: Optional[str] = Field(None, description="ISO date, year, or 'Present'")
    location: Optional[str] = None
    description: Optional[str] = None


class EducationItem(BaseModel):
    degree: Optional[str] = None
    field: Optional[str] = None
    institution: Optional[str] = None
    start: Optional[str] = None
    end: Optional[str] = None
    location: Optional[str] = None


class Skill(BaseModel):
    name: str
    level: Optional[str] = Field(None, description="Proficiency level, e.g. Beginner/Expert or 1-5")
    years: Optional[float] = Field(None, description="Years of experience")


class Resume(BaseModel):
    personal: Personal = Personal()
    experience: List[ExperienceItem] = []
    education: List[EducationItem] = []
    skills: List[Skill] = []
    certifications: Optional[List[str]] = None
    awards: Optional[List[str]] = None

    # Parser metadata
    confidence: Optional[float] = Field(None, ge=0, le=1)
    needs_review: bool = False

    model_config = {
        "title": "ResumeSchema",
        "description": "Structured schema for parsed résumés/CVs.",
    }


__all__ = [
    "Personal",
    "ExperienceItem",
    "EducationItem",
    "Skill",
    "Resume",
] 