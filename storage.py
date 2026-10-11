"""CSV persistence helpers for goals and savings transactions."""
from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent / "data"
GOALS_FILE = DATA_DIR / "goals.csv"
TRANSACTIONS_FILE = DATA_DIR / "transactions.csv"

GOAL_COLUMNS = ["goal_id", "name", "target_amount", "target_date", "created_date"]
TRANSACTION_COLUMNS = [
    "transaction_id", "goal_id", "date", "transaction_type", "amount", "note"
]

def _ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)

def load_csv(path, columns):
    """Load a CSV, returning an empty correctly-shaped DataFrame if missing/empty."""
    _ensure_data_dir()
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame(columns=columns)
    try:
        df = pd.read_csv(path, dtype={"goal_id": str, "transaction_id": str})
        for column in columns:
            if column not in df.columns:
                df[column] = ""
        return df[columns]
    except (pd.errors.EmptyDataError, pd.errors.ParserError, OSError) as exc:
        raise ValueError(f"Could not read {path.name}: {exc}") from exc

def save_csv(df, path, columns):
    """Persist a DataFrame to CSV, preserving the defined column order."""
    _ensure_data_dir()
    try:
        df.reindex(columns=columns).to_csv(path, index=False)
    except OSError as exc:
        raise ValueError(f"Could not save {path.name}: {exc}") from exc

def load_goals():
    return load_csv(GOALS_FILE, GOAL_COLUMNS)

def save_goals(df):
    save_csv(df, GOALS_FILE, GOAL_COLUMNS)

def load_transactions():
    return load_csv(TRANSACTIONS_FILE, TRANSACTION_COLUMNS)

def save_transactions(df):
    save_csv(df, TRANSACTIONS_FILE, TRANSACTION_COLUMNS)
