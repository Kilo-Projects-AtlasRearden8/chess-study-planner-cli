# Chess Study Planner CLI

A Python command-line tool for planning chess opening and endgame study sessions, logging practice, and tracking progress with local JSON storage and CSV export.

Built by **Asdale Dynamics, LLC** — beginner-friendly AI education, books, guides, and practical tools. Learn more at [dylanasdale.github.io](https://dylanasdale.github.io).

A fan project with no game assets. MIT licensed.

## Features

- **Plan study sessions** — create opening and endgame sessions with named positions
- **Log practice** — record duration, positions studied, correct/total attempts, and notes
- **Track progress** — view overall and per-type accuracy, total minutes, positions studied
- **Export to CSV** — export practice logs and progress statistics
- **Local-first JSON storage** — all data stored locally in JSON files under `data/`
- **Tested** — unit tests cover accuracy math, session CRUD, storage, and CSV export

## Installation

```bash
# Clone or download this repository
cd chess-study-planner-cli

# Install dependencies
pip install -r requirements.txt

# Run the CLI
python -m chess_study.cli --help

# Or run directly
python chess_study_main.py --help
```

## Usage

### Create a session

```bash
# Opening session
python -m chess_study.cli session add "Italian Game" opening --description "1. e4 e5 2. Nf3 Nc6 3. Bc4" --positions "e4,e5,Nf3,Nc6,Bc4"

# Endgame session
python -m chess_study.cli session add "King and Pawn vs King" endgame --description "Basic king and pawn endgame" --positions "KPvK"
```

### List sessions

```bash
python -m chess_study.cli session list
python -m chess_study.cli session list --verbose
```

### Show a session

```bash
python -m chess_study.cli session show <session-id>
```

### Log practice

```bash
python -m chess_study.cli log add <session-id> --duration 30 --positions 5 --correct 8 --attempts 10 --notes "Felt sharp today"
```

### List practice logs

```bash
python -m chess_study.cli log list
python -m chess_study.cli log list --session-id <session-id>
```

### View progress

```bash
python -m chess_study.cli progress
```

### Export to CSV

```bash
python -m chess_study.cli export --logs data/practice_logs.csv --progress data/progress.csv
```

## Data Storage

All data is stored locally in JSON files:

- `data/sessions.json` — study sessions
- `data/practice_logs.json` — practice logs

## Running Tests

```bash
pip install pytest
pytest tests/ -v
```

## License

MIT License. Copyright (c) 2026 Asdale Dynamics, LLC.

## About

This is a fan project by Asdale Dynamics, LLC — a beginner-friendly AI education company founded by Dylan Asdale, a registered nurse turned AI author. Dylan's book *The Massive AI Manual* and hub site dylanasdale.github.io explain AI "like a friend would": plain English, step by step, never condescending. This chess tool is part of the LLC's open-source apps and templates line.

No game assets are included. No secrets, API keys, or personal data are stored.