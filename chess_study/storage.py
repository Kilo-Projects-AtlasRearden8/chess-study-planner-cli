"""Storage layer for chess study data."""
import json
import csv
import os
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from chess_study.models import StudySession, PracticeLog, ProgressStats, SessionType


class Storage:
    """Handles data persistence for sessions and practice logs."""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.sessions_file = self.data_dir / "sessions.json"
        self.logs_file = self.data_dir / "practice_logs.json"

    # Session methods
    def load_sessions(self) -> List[StudySession]:
        """Load all study sessions from JSON."""
        if not self.sessions_file.exists():
            return []
        with open(self.sessions_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [StudySession.from_dict(item) for item in data]

    def save_sessions(self, sessions: List[StudySession]) -> None:
        """Save all study sessions to JSON."""
        with open(self.sessions_file, "w", encoding="utf-8") as f:
            json.dump([s.to_dict() for s in sessions], f, indent=2)

    def get_session(self, session_id: str) -> Optional[StudySession]:
        """Get a session by ID."""
        sessions = self.load_sessions()
        for s in sessions:
            if s.id == session_id:
                return s
        return None

    def add_session(self, session: StudySession) -> None:
        """Add a new session."""
        sessions = self.load_sessions()
        sessions.append(session)
        self.save_sessions(sessions)

    def update_session(self, session: StudySession) -> bool:
        """Update an existing session."""
        sessions = self.load_sessions()
        for i, s in enumerate(sessions):
            if s.id == session.id:
                session.updated_at = datetime.now().isoformat()
                sessions[i] = session
                self.save_sessions(sessions)
                return True
        return False

    def delete_session(self, session_id: str) -> bool:
        """Delete a session by ID."""
        sessions = self.load_sessions()
        original_len = len(sessions)
        sessions = [s for s in sessions if s.id != session_id]
        if len(sessions) < original_len:
            self.save_sessions(sessions)
            return True
        return False

    # Practice log methods
    def load_logs(self) -> List[PracticeLog]:
        """Load all practice logs from JSON."""
        if not self.logs_file.exists():
            return []
        with open(self.logs_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return [PracticeLog.from_dict(item) for item in data]

    def save_logs(self, logs: List[PracticeLog]) -> None:
        """Save all practice logs to JSON."""
        with open(self.logs_file, "w", encoding="utf-8") as f:
            json.dump([log.to_dict() for log in logs], f, indent=2)

    def add_log(self, log: PracticeLog) -> None:
        """Add a new practice log."""
        logs = self.load_logs()
        logs.append(log)
        self.save_logs(logs)

    def get_logs_for_session(self, session_id: str) -> List[PracticeLog]:
        """Get all logs for a specific session."""
        logs = self.load_logs()
        return [log for log in logs if log.session_id == session_id]

    # Export methods
    def export_logs_csv(self, output_path: str) -> None:
        """Export practice logs to CSV."""
        logs = self.load_logs()
        if not logs:
            return

        fieldnames = [
            "id", "session_id", "session_name", "session_type", "date",
            "duration_minutes", "positions_studied", "correct", "total_attempts",
            "accuracy", "notes", "created_at"
        ]

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for log in logs:
                row = log.to_dict()
                row["accuracy"] = log.accuracy
                writer.writerow(row)

    def export_progress_csv(self, output_path: str) -> None:
        """Export progress stats to CSV."""
        stats = self.calculate_progress()
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(stats.to_csv_row().keys()))
            writer.writeheader()
            writer.writerow(stats.to_csv_row())

    # Progress calculation
    def calculate_progress(self) -> ProgressStats:
        """Calculate aggregated progress statistics."""
        logs = self.load_logs()
        stats = ProgressStats()

        for log in logs:
            stats.total_sessions += 1
            stats.total_minutes += log.duration_minutes
            stats.total_positions += log.positions_studied
            stats.total_correct += log.correct
            stats.total_attempts += log.total_attempts

            type_key = log.session_type.value
            if type_key not in stats.by_type:
                stats.by_type[type_key] = {"sessions": 0, "minutes": 0, "correct": 0, "attempts": 0}

            stats.by_type[type_key]["sessions"] += 1
            stats.by_type[type_key]["minutes"] += log.duration_minutes
            stats.by_type[type_key]["correct"] += log.correct
            stats.by_type[type_key]["attempts"] += log.total_attempts

        # Calculate accuracy for each type
        for type_key, data in stats.by_type.items():
            if data["attempts"] > 0:
                data["accuracy"] = round((data["correct"] / data["attempts"]) * 100, 2)
            else:
                data["accuracy"] = 0.0

        return stats