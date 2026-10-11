"""Matplotlib visual reports."""
import matplotlib.pyplot as plt
from analytics import monthly_totals, cumulative_savings

def show_monthly_chart(goal_id=""):
    df = monthly_totals(goal_id)
    if df.empty:
        raise ValueError("Add transactions first to create a monthly report.")
    ax = df.set_index("month")[["deposits", "withdrawals"]].plot(kind="bar", figsize=(8, 4))
    ax.set_title("Monthly Deposits vs Withdrawals")
    ax.set_xlabel("Month")
    ax.set_ylabel("Amount (₹)")
    ax.legend(["Deposits", "Withdrawals"])
    ax.tick_params(axis="x", rotation=35)
    ax.figure.tight_layout()
    plt.show()

def show_growth_chart(goal_id=""):
    df = cumulative_savings(goal_id)
    if df.empty:
        raise ValueError("Add transactions first to create a savings growth report.")
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(df["date"], df["net_savings"], marker="o", label="Net savings")
    ax.set_title("Savings Growth Over Time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Net savings (₹)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.autofmt_xdate()
    fig.tight_layout()
    plt.show()
