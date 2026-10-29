"""Data models for chess study planner."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
import json


class SessionType(Enum):
    """Type of study session."""
    OPENING = "opening"
    ENDGAME = "endgame"


@dataclass
class StudySession:
    """A planned study session."""
    id: str
    name: str
    session_type: SessionType
    description: str = ""
    positions: list = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "session_type": self.session_type.value,
            "description": self.description,
            "positions": self.positions,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "StudySession":
        """Create from dictionary."""
        data = data.copy()
        data["session_type"] = SessionType(data["session_type"])
        return cls(**data)


@dataclass
class PracticeLog:
    """A logged practice session."""
    id: str
    session_id: str
    session_name: str
    session_type: SessionType
    date: str
    duration_minutes: int
    positions_studied: int
    correct: int
    total_attempts: int
    notes: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    @property
    def accuracy(self) -> float:
        """Calculate accuracy percentage."""
        if self.total_attempts == 0:
            return 0.0
        return round((self.correct / self.total_attempts) * 100, 2)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "session_name": self.session_name,
            "session_type": self.session_type.value,
            "date": self.date,
            "duration_minutes": self.duration_minutes,
            "positions_studied": self.positions_studied,
            "correct": self.correct,
            "total_attempts": self.total_attempts,
            "notes": self.notes,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PracticeLog":
        """Create from dictionary."""
        data = data.copy()
        data["session_type"] = SessionType(data["session_type"])
        return cls(**data)


@dataclass
class ProgressStats:
    """Aggregated progress statistics."""
    total_sessions: int = 0
    total_minutes: int = 0
    total_positions: int = 0
    total_correct: int = 0
    total_attempts: int = 0
    by_type: dict = field(default_factory=dict)

    @property
    def overall_accuracy(self) -> float:
        """Calculate overall accuracy percentage."""
        if self.total_attempts == 0:
            return 0.0
        return round((self.total_correct / self.total_attempts) * 100, 2)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "total_sessions": self.total_sessions,
            "total_minutes": self.total_minutes,
            "total_positions": self.total_positions,
            "total_correct": self.total_correct,
            "total_attempts": self.total_attempts,
            "overall_accuracy": self.overall_accuracy,
            "by_type": self.by_type,
        }

    def to_csv_row(self) -> dict:
        """Convert to CSV row format."""
        return {
            "total_sessions": self.total_sessions,
            "total_minutes": self.total_minutes,
            "total_positions": self.total_positions,
            "total_correct": self.total_correct,
            "total_attempts": self.total_attempts,
            "overall_accuracy": self.overall_accuracy,
            "opening_sessions": self.by_type.get("opening", {}).get("sessions", 0),
            "opening_minutes": self.by_type.get("opening", {}).get("minutes", 0),
            "opening_accuracy": self.by_type.get("opening", {}).get("accuracy", 0.0),
            "endgame_sessions": self.by_type.get("endgame", {}).get("sessions", 0),
            "endgame_minutes": self.by_type.get("endgame", {}).get("minutes", 0),
            "endgame_accuracy": self.by_type.get("endgame", {}).get("accuracy", 0.0),
        }