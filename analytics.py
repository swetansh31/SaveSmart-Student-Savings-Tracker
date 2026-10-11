"""Pandas/NumPy-based savings analytics."""
import numpy as np
import pandas as pd
from storage import load_goals, load_transactions

def transaction_frame():
    df = load_transactions()
    goals = load_goals()
    if df.empty:
        return df.assign(goal_name=pd.Series(dtype=str), signed_amount=pd.Series(dtype=float))
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["goal_id"] = df["goal_id"].astype(str)
    df["goal_name"] = df["goal_id"].map(
        dict(zip(goals["goal_id"].astype(str), goals["name"].astype(str)))
    ).fillna("Unknown goal")
    df["signed_amount"] = np.where(df["transaction_type"].eq("Deposit"), df["amount"], -df["amount"])
    return df

def goal_summary(goal_id):
    goals = load_goals()
    selected = goals[goals["goal_id"].astype(str) == str(goal_id)]
    if selected.empty:
        raise ValueError("Goal not found.")
    goal = selected.iloc[0]
    tx = transaction_frame()
    tx = tx[tx["goal_id"].astype(str) == str(goal_id)] if not tx.empty else tx
    deposits = float(tx.loc[tx["transaction_type"] == "Deposit", "amount"].sum()) if not tx.empty else 0.0
    withdrawals = float(tx.loc[tx["transaction_type"] == "Withdrawal", "amount"].sum()) if not tx.empty else 0.0
    net = deposits - withdrawals
    target = float(goal["target_amount"])
    progress = max(0.0, min(100.0, net / target * 100)) if target else 0.0
    if not tx.empty:
        monthly = tx.assign(month=tx["date"].dt.to_period("M")).groupby("month")["signed_amount"].sum()
        positive_months = monthly[monthly > 0]
        pace = float(positive_months.mean()) if not positive_months.empty else 0.0
    else:
        pace = 0.0
    remaining = max(0.0, target - net)
    months = int(np.ceil(remaining / pace)) if pace > 0 and remaining > 0 else (0 if remaining == 0 else None)
    return {
        "name": str(goal["name"]), "target": target, "deposits": deposits,
        "withdrawals": withdrawals, "net": net, "progress": progress,
        "remaining": remaining, "pace": pace, "months": months,
        "target_date": str(goal["target_date"]),
    }

def filter_transactions(goal_id="", transaction_type="All", start_date="", end_date=""):
    df = transaction_frame()
    if df.empty:
        return df
    if goal_id:
        df = df[df["goal_id"].astype(str) == str(goal_id)]
    if transaction_type != "All":
        df = df[df["transaction_type"] == transaction_type]
    if start_date:
        df = df[df["date"] >= pd.Timestamp(start_date)]
    if end_date:
        df = df[df["date"] <= pd.Timestamp(end_date)]
    return df.sort_values("date", ascending=False)

def monthly_totals(goal_id=""):
    df = transaction_frame()
    if df.empty:
        return pd.DataFrame(columns=["month", "deposits", "withdrawals", "net"])
    if goal_id:
        df = df[df["goal_id"].astype(str) == str(goal_id)]
    df["month"] = df["date"].dt.to_period("M").astype(str)
    grouped = df.pivot_table(index="month", columns="transaction_type", values="amount",
                             aggfunc="sum", fill_value=0)
    for kind in ["Deposit", "Withdrawal"]:
        if kind not in grouped.columns:
            grouped[kind] = 0.0
    result = grouped.rename(columns={"Deposit": "deposits", "Withdrawal": "withdrawals"})
    result["net"] = result["deposits"] - result["withdrawals"]
    return result.reset_index().sort_values("month")

def cumulative_savings(goal_id=""):
    df = transaction_frame()
    if df.empty:
        return pd.DataFrame(columns=["date", "net_savings"])
    if goal_id:
        df = df[df["goal_id"].astype(str) == str(goal_id)]
    if df.empty:
        return pd.DataFrame(columns=["date", "net_savings"])
    daily = df.groupby("date", as_index=False)["signed_amount"].sum().sort_values("date")
    daily["net_savings"] = daily["signed_amount"].cumsum()
    return daily[["date", "net_savings"]]
