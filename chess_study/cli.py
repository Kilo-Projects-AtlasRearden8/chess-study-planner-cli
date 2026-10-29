"""CLI commands for chess study planner."""
import argparse
import sys
import uuid
from datetime import date
from typing import Optional

from chess_study.models import StudySession, PracticeLog, SessionType
from chess_study.storage import Storage


def generate_id() -> str:
    """Generate a short unique ID."""
    return uuid.uuid4().hex[:8]


def cmd_session_add(args: argparse.Namespace, storage: Storage) -> int:
    """Add a new study session."""
    session_type = SessionType(args.type)
    session = StudySession(
        id=generate_id(),
        name=args.name,
        session_type=session_type,
        description=args.description or "",
        positions=args.positions.split(",") if args.positions else [],
    )
    storage.add_session(session)
    print(f"Created session: {session.name} ({session.id}) [{session_type.value}]")
    return 0


def cmd_session_list(args: argparse.Namespace, storage: Storage) -> int:
    """List all study sessions."""
    sessions = storage.load_sessions()
    if not sessions:
        print("No sessions found.")
        return 0

    for s in sessions:
        positions = f", {len(s.positions)} positions" if s.positions else ""
        print(f"  {s.id}  {s.name} [{s.session_type.value}]{positions}")
        if args.verbose and s.description:
            print(f"    {s.description}")
    return 0


def cmd_session_show(args: argparse.Namespace, storage: Storage) -> int:
    """Show details of a specific session."""
    session = storage.get_session(args.id)
    if not session:
        print(f"Session not found: {args.id}")
        return 1

    print(f"ID: {session.id}")
    print(f"Name: {session.name}")
    print(f"Type: {session.session_type.value}")
    print(f"Description: {session.description or '(none)'}")
    print(f"Positions: {', '.join(session.positions) if session.positions else '(none)'}")
    print(f"Created: {session.created_at}")
    print(f"Updated: {session.updated_at}")
    return 0


def cmd_session_delete(args: argparse.Namespace, storage: Storage) -> int:
    """Delete a study session."""
    if storage.delete_session(args.id):
        print(f"Deleted session: {args.id}")
        return 0
    print(f"Session not found: {args.id}")
    return 1


def cmd_log_add(args: argparse.Namespace, storage: Storage) -> int:
    """Log a practice session."""
    session = storage.get_session(args.session_id)
    if not session:
        print(f"Session not found: {args.session_id}")
        return 1

    practice_date = args.date or date.today().isoformat()

    log = PracticeLog(
        id=generate_id(),
        session_id=session.id,
        session_name=session.name,
        session_type=session.session_type,
        date=practice_date,
        duration_minutes=args.duration,
        positions_studied=args.positions,
        correct=args.correct,
        total_attempts=args.attempts,
        notes=args.notes or "",
    )
    storage.add_log(log)
    print(f"Logged practice: {session.name} on {practice_date} ({log.duration_minutes} min, {log.accuracy}% accuracy)")
    return 0


def cmd_log_list(args: argparse.Namespace, storage: Storage) -> int:
    """List practice logs."""
    logs = storage.load_logs()
    if args.session_id:
        logs = [log for log in logs if log.session_id == args.session_id]

    if not logs:
        print("No practice logs found.")
        return 0

    for log in logs:
        print(f"  {log.id}  {log.date}  {log.session_name} [{log.session_type.value}]  "
              f"{log.duration_minutes}min  {log.positions_studied}pos  {log.accuracy}%")
    return 0


def cmd_progress(args: argparse.Namespace, storage: Storage) -> int:
    """Show progress statistics."""
    stats = storage.calculate_progress()

    print("=== Progress Summary ===")
    print(f"Total Sessions:  {stats.total_sessions}")
    print(f"Total Minutes:   {stats.total_minutes}")
    print(f"Total Positions: {stats.total_positions}")
    print(f"Total Attempts:  {stats.total_attempts}")
    print(f"Total Correct:   {stats.total_correct}")
    print(f"Overall Accuracy: {stats.overall_accuracy}%")
    print()

    if stats.by_type:
        print("By Type:")
        for type_key, data in stats.by_type.items():
            print(f"  {type_key.capitalize()}: {data['sessions']} sessions, "
                  f"{data['minutes']} min, {data['accuracy']}% accuracy")
    return 0


def cmd_export(args: argparse.Namespace, storage: Storage) -> int:
    """Export data to CSV."""
    if args.logs:
        storage.export_logs_csv(args.logs)
        print(f"Exported practice logs to: {args.logs}")
    if args.progress:
        storage.export_progress_csv(args.progress)
        print(f"Exported progress to: {args.progress}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    parser = argparse.ArgumentParser(
        prog="chess-study",
        description="Chess Study Planner - Plan openings, endgames, log practice, track progress",
    )
    parser.add_argument("--version", action="version", version="%(prog)s 1.0.0")

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Session commands
    session_parser = subparsers.add_parser("session", help="Manage study sessions")
    session_sub = session_parser.add_subparsers(dest="session_cmd", required=True)

    add_session = session_sub.add_parser("add", help="Add a new session")
    add_session.add_argument("name", help="Session name")
    add_session.add_argument("type", choices=["opening", "endgame"], help="Session type")
    add_session.add_argument("--description", "-d", help="Session description")
    add_session.add_argument("--positions", "-p", help="Comma-separated position names")
    add_session.set_defaults(func=cmd_session_add)

    list_session = session_sub.add_parser("list", help="List all sessions")
    list_session.add_argument("--verbose", "-v", action="store_true", help="Show descriptions")
    list_session.set_defaults(func=cmd_session_list)

    show_session = session_sub.add_parser("show", help="Show session details")
    show_session.add_argument("id", help="Session ID")
    show_session.set_defaults(func=cmd_session_show)

    del_session = session_sub.add_parser("delete", help="Delete a session")
    del_session.add_argument("id", help="Session ID")
    del_session.set_defaults(func=cmd_session_delete)

    # Log commands
    log_parser = subparsers.add_parser("log", help="Manage practice logs")
    log_sub = log_parser.add_subparsers(dest="log_cmd", required=True)

    add_log = log_sub.add_parser("add", help="Add a practice log")
    add_log.add_argument("session_id", help="Session ID")
    add_log.add_argument("--date", help="Practice date (YYYY-MM-DD), defaults to today")
    add_log.add_argument("--duration", type=int, required=True, help="Duration in minutes")
    add_log.add_argument("--positions", type=int, required=True, help="Positions studied")
    add_log.add_argument("--correct", type=int, required=True, help="Correct attempts")
    add_log.add_argument("--attempts", type=int, required=True, help="Total attempts")
    add_log.add_argument("--notes", "-n", help="Notes")
    add_log.set_defaults(func=cmd_log_add)

    list_log = log_sub.add_parser("list", help="List practice logs")
    list_log.add_argument("--session-id", help="Filter by session ID")
    list_log.set_defaults(func=cmd_log_list)

    # Progress command
    progress_parser = subparsers.add_parser("progress", help="Show progress statistics")
    progress_parser.set_defaults(func=cmd_progress)

    # Export command
    export_parser = subparsers.add_parser("export", help="Export data to CSV")
    export_parser.add_argument("--logs", help="Export practice logs to CSV file")
    export_parser.add_argument("--progress", help="Export progress stats to CSV file")
    export_parser.set_defaults(func=cmd_export)

    return parser


def main(argv: Optional[list] = None) -> int:
    """Main entry point."""
    parser = build_parser()
    args = parser.parse_args(argv)

    storage = Storage()
    return args.func(args, storage)


if __name__ == "__main__":
    sys.exit(main())