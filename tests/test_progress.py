"""Tests for chess study progress math and storage."""
import json
import os
import tempfile
import pytest

from chess_study.models import (
    StudySession, PracticeLog, ProgressStats, SessionType
)
from chess_study.storage import Storage


# --- StudySession tests ---

def test_study_session_to_from_dict():
    session = StudySession(
        id="abc12345",
        name="Italian Game",
        session_type=SessionType.OPENING,
        description="1. e4 e5 2. Nf3 Nc6 3. Bc4",
        positions=["e4", "Nf3", "Bc4"],
    )
    data = session.to_dict()
    restored = StudySession.from_dict(data)
    assert restored.id == session.id
    assert restored.name == session.name
    assert restored.session_type == session.session_type
    assert restored.description == session.description
    assert restored.positions == session.positions


# --- PracticeLog accuracy tests ---

def test_practice_log_accuracy_zero_attempts():
    log = PracticeLog(
        id="abc12345",
        session_id="sess1",
        session_name="Test",
        session_type=SessionType.OPENING,
        date="2026-01-01",
        duration_minutes=30,
        positions_studied=5,
        correct=0,
        total_attempts=0,
    )
    assert log.accuracy == 0.0


def test_practice_log_accuracy_perfect():
    log = PracticeLog(
        id="abc12345",
        session_id="sess1",
        session_name="Test",
        session_type=SessionType.OPENING,
        date="2026-01-01",
        duration_minutes=30,
        positions_studied=5,
        correct=10,
        total_attempts=10,
    )
    assert log.accuracy == 100.0


def test_practice_log_accuracy_half():
    log = PracticeLog(
        id="abc12345",
        session_id="sess1",
        session_name="Test",
        session_type=SessionType.OPENING,
        date="2026-01-01",
        duration_minutes=30,
        positions_studied=5,
        correct=5,
        total_attempts=10,
    )
    assert log.accuracy == 50.0


def test_practice_log_accuracy_third():
    log = PracticeLog(
        id="abc12345",
        session_id="sess1",
        session_name="Test",
        session_type=SessionType.ENDGAME,
        date="2026-01-01",
        duration_minutes=30,
        positions_studied=3,
        correct=1,
        total_attempts=3,
    )
    assert log.accuracy == 33.33


# --- ProgressStats tests ---

def test_progress_stats_empty():
    stats = ProgressStats()
    assert stats.overall_accuracy == 0.0
    assert stats.total_sessions == 0
    assert stats.total_attempts == 0


def test_progress_stats_overall_accuracy():
    stats = ProgressStats()
    stats.total_attempts = 20
    stats.total_correct = 15
    assert stats.overall_accuracy == 75.0


def test_progress_stats_by_type_accuracy():
    stats = ProgressStats()
    stats.by_type = {
        "opening": {"sessions": 2, "minutes": 60, "correct": 8, "attempts": 10},
        "endgame": {"sessions": 1, "minutes": 30, "correct": 4, "attempts": 4},
    }
    for type_key, data in stats.by_type.items():
        if data["attempts"] > 0:
            data["accuracy"] = round((data["correct"] / data["attempts"]) * 100, 2)
        else:
            data["accuracy"] = 0.0
    assert stats.by_type["opening"]["accuracy"] == 80.0
    assert stats.by_type["endgame"]["accuracy"] == 100.0


# --- Storage tests ---

@pytest.fixture
def temp_storage():
    tmpdir = tempfile.mkdtemp()
    storage = Storage(data_dir=tmpdir)
    yield storage
    # cleanup
    import shutil
    shutil.rmtree(tmpdir)


def test_storage_session_crud(temp_storage):
    session = StudySession(
        id="abc12345",
        name="Sicilian Defense",
        session_type=SessionType.OPENING,
        description="1. e4 c5",
        positions=["e4", "c5"],
    )
    temp_storage.add_session(session)
    sessions = temp_storage.load_sessions()
    assert len(sessions) == 1
    assert sessions[0].name == "Sicilian Defense"

    retrieved = temp_storage.get_session("abc12345")
    assert retrieved is not None
    assert retrieved.name == "Sicilian Defense"

    session.name = "Sicilian Defense Updated"
    temp_storage.update_session(session)
    retrieved = temp_storage.get_session("abc12345")
    assert retrieved.name == "Sicilian Defense Updated"

    assert temp_storage.delete_session("abc12345") is True
    assert temp_storage.get_session("abc12345") is None


def test_storage_log_crud(temp_storage):
    session = StudySession(
        id="abc12345",
        name="King Pawn Opening",
        session_type=SessionType.OPENING,
    )
    temp_storage.add_session(session)

    log = PracticeLog(
        id="log12345",
        session_id="abc12345",
        session_name="King Pawn Opening",
        session_type=SessionType.OPENING,
        date="2026-01-01",
        duration_minutes=30,
        positions_studied=5,
        correct=4,
        total_attempts=5,
        notes="Good session",
    )
    temp_storage.add_log(log)
    logs = temp_storage.load_logs()
    assert len(logs) == 1
    assert logs[0].accuracy == 80.0

    session_logs = temp_storage.get_logs_for_session("abc12345")
    assert len(session_logs) == 1
    assert session_logs[0].id == "log12345"


def test_storage_calculate_progress(temp_storage):
    s1 = StudySession(id="s1", name="Opening 1", session_type=SessionType.OPENING)
    s2 = StudySession(id="s2", name="Endgame 1", session_type=SessionType.ENDGAME)
    temp_storage.add_session(s1)
    temp_storage.add_session(s2)

    log1 = PracticeLog(
        id="l1", session_id="s1", session_name="Opening 1",
        session_type=SessionType.OPENING, date="2026-01-01",
        duration_minutes=30, positions_studied=5, correct=8, total_attempts=10,
    )
    log2 = PracticeLog(
        id="l2", session_id="s2", session_name="Endgame 1",
        session_type=SessionType.ENDGAME, date="2026-01-02",
        duration_minutes=20, positions_studied=3, correct=4, total_attempts=5,
    )
    temp_storage.add_log(log1)
    temp_storage.add_log(log2)

    stats = temp_storage.calculate_progress()
    assert stats.total_sessions == 2
    assert stats.total_minutes == 50
    assert stats.total_positions == 8
    assert stats.total_correct == 12
    assert stats.total_attempts == 15
    assert stats.overall_accuracy == 80.0
    assert "opening" in stats.by_type
    assert "endgame" in stats.by_type


def test_storage_export_progress_csv(temp_storage):
    s1 = StudySession(id="s1", name="Opening 1", session_type=SessionType.OPENING)
    temp_storage.add_session(s1)
    log1 = PracticeLog(
        id="l1", session_id="s1", session_name="Opening 1",
        session_type=SessionType.OPENING, date="2026-01-01",
        duration_minutes=30, positions_studied=5, correct=8, total_attempts=10,
    )
    temp_storage.add_log(log1)

    csv_path = os.path.join(temp_storage.data_dir, "progress.csv")
    temp_storage.export_progress_csv(csv_path)
    assert os.path.exists(csv_path)
    with open(csv_path, "r") as f:
        content = f.read()
    assert "total_sessions" in content
    assert "overall_accuracy" in content


def test_storage_export_logs_csv(temp_storage):
    s1 = StudySession(id="s1", name="Opening 1", session_type=SessionType.OPENING)
    temp_storage.add_session(s1)
    log1 = PracticeLog(
        id="l1", session_id="s1", session_name="Opening 1",
        session_type=SessionType.OPENING, date="2026-01-01",
        duration_minutes=30, positions_studied=5, correct=8, total_attempts=10,
    )
    temp_storage.add_log(log1)

    csv_path = os.path.join(temp_storage.data_dir, "logs.csv")
    temp_storage.export_logs_csv(csv_path)
    assert os.path.exists(csv_path)
    with open(csv_path, "r") as f:
        content = f.read()
    assert "accuracy" in content
    assert "session_id" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])