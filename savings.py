"""Business rules for savings goals and transactions."""
from datetime import date, datetime
import uuid
import pandas as pd
from storage import load_goals, save_goals, load_transactions, save_transactions

def _money(value, field="Amount"):
    try:
        amount = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be a valid number.") from exc
    if amount <= 0:
        raise ValueError(f"{field} must be greater than zero.")
    if not amount < float("inf"):
        raise ValueError(f"{field} must be a finite number.")
    return round(amount, 2)

def _valid_date(value, field="Date"):
    try:
        return datetime.strptime(str(value).strip(), "%Y-%m-%d").date().isoformat()
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must use YYYY-MM-DD format.") from exc

def create_goal(name, target_amount, target_date):
    name = str(name).strip()
    if not name:
        raise ValueError("Goal name cannot be empty.")
    if len(name) > 80:
        raise ValueError("Goal name must be 80 characters or fewer.")
    amount = _money(target_amount, "Target amount")
    target_date = _valid_date(target_date, "Target date")
    goals = load_goals()
    goals = pd.concat([goals, pd.DataFrame([{
        "goal_id": uuid.uuid4().hex[:10],
        "name": name,
        "target_amount": amount,
        "target_date": target_date,
        "created_date": date.today().isoformat(),
    }])], ignore_index=True)
    save_goals(goals)
    return goals.iloc[-1].to_dict()

def add_transaction(goal_id, transaction_date, transaction_type, amount, note=""):
    goals = load_goals()
    if goal_id not in goals["goal_id"].astype(str).tolist():
        raise ValueError("Please select an existing savings goal.")
    transaction_date = _valid_date(transaction_date, "Transaction date")
    transaction_type = str(transaction_type).strip().title()
    if transaction_type not in {"Deposit", "Withdrawal"}:
        raise ValueError("Transaction type must be Deposit or Withdrawal.")
    amount = _money(amount)
    note = str(note).strip()[:160]
    transactions = load_transactions()
    transactions = pd.concat([transactions, pd.DataFrame([{
        "transaction_id": uuid.uuid4().hex[:10],
        "goal_id": str(goal_id),
        "date": transaction_date,
        "transaction_type": transaction_type,
        "amount": amount,
        "note": note,
    }])], ignore_index=True)
    save_transactions(transactions)
    return transactions.iloc[-1].to_dict()

def delete_transaction(transaction_id):
    transactions = load_transactions()
    updated = transactions[transactions["transaction_id"].astype(str) != str(transaction_id)]
    if len(updated) == len(transactions):
        raise ValueError("Transaction was not found.")
    save_transactions(updated)
