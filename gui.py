"""Simple Tkinter GUI for SaveSmart."""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
import pandas as pd
from storage import load_goals, load_transactions
from savings import create_goal, add_transaction, delete_transaction
from analytics import goal_summary, filter_transactions
from reports import show_monthly_chart, show_growth_chart

class SaveSmartApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("SaveSmart - Student Savings Tracker")
        self.geometry("1050x700")
        self.minsize(900, 600)
        self.configure(padx=12, pady=12)
        self._build_ui()
        self.refresh_all()

    def _build_ui(self):
        ttk.Label(self, text="SaveSmart: Student Savings Tracker",
                  font=("Arial", 18, "bold")).pack(anchor="w", pady=(0, 10))
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill="both", expand=True)
        self.dashboard = ttk.Frame(self.tabs, padding=10)
        self.goals_tab = ttk.Frame(self.tabs, padding=10)
        self.transactions_tab = ttk.Frame(self.tabs, padding=10)
        self.reports_tab = ttk.Frame(self.tabs, padding=10)
        self.tabs.add(self.dashboard, text="Dashboard")
        self.tabs.add(self.goals_tab, text="Savings Goals")
        self.tabs.add(self.transactions_tab, text="Transactions")
        self.tabs.add(self.reports_tab, text="Reports")
        self._build_dashboard()
        self._build_goals()
        self._build_transactions()
        self._build_reports()

    def _build_dashboard(self):
        self.summary_box = ttk.LabelFrame(self.dashboard, text="Goal Progress", padding=10)
        self.summary_box.pack(fill="x", pady=5)
        self.goal_pick = ttk.Combobox(self.summary_box, state="readonly", width=35)
        self.goal_pick.pack(side="left", padx=(0, 10))
        self.goal_pick.bind("<<ComboboxSelected>>", lambda _e: self.update_summary())
        ttk.Button(self.summary_box, text="Refresh", command=self.refresh_all).pack(side="left")
        self.summary_text = tk.Text(self.dashboard, height=12, wrap="word", state="disabled")
        self.summary_text.pack(fill="both", expand=True, pady=10)
        ttk.Label(self.dashboard, text="Estimated months use the average of positive net-saving months; this is an estimate, not a guarantee.",
                  wraplength=900).pack(anchor="w")

    def _build_goals(self):
        form = ttk.LabelFrame(self.goals_tab, text="Create a savings goal", padding=10)
        form.pack(fill="x")
        self.goal_name = tk.StringVar()
        self.goal_target = tk.StringVar()
        self.goal_date = tk.StringVar(value=date.today().replace(year=date.today().year + 1).isoformat())
        for col, (label, var, width) in enumerate([
            ("Goal name", self.goal_name, 25), ("Target amount (₹)", self.goal_target, 15),
            ("Target date (YYYY-MM-DD)", self.goal_date, 18)]):
            ttk.Label(form, text=label).grid(row=0, column=col, sticky="w", padx=4)
            ttk.Entry(form, textvariable=var, width=width).grid(row=1, column=col, padx=4, pady=4, sticky="w")
        ttk.Button(form, text="Add Goal", command=self.on_add_goal).grid(row=1, column=3, padx=8)
        ttk.Label(self.goals_tab, text="Create goals here, then record deposits or withdrawals in the Transactions tab.").pack(anchor="w", pady=12)

    def _build_transactions(self):
        form = ttk.LabelFrame(self.transactions_tab, text="Record transaction", padding=10)
        form.pack(fill="x")
        self.tx_goal = ttk.Combobox(form, state="readonly", width=25)
        self.tx_type = ttk.Combobox(form, state="readonly", values=["Deposit", "Withdrawal"], width=12)
        self.tx_type.set("Deposit")
        self.tx_date = tk.StringVar(value=date.today().isoformat())
        self.tx_amount = tk.StringVar()
        self.tx_note = tk.StringVar()
        fields = [
            ("Goal", self.tx_goal), ("Type", self.tx_type),
            ("Date (YYYY-MM-DD)", ttk.Entry(form, textvariable=self.tx_date, width=14)),
            ("Amount (₹)", ttk.Entry(form, textvariable=self.tx_amount, width=12)),
            ("Note", ttk.Entry(form, textvariable=self.tx_note, width=22)),
        ]
        for i, (label, widget) in enumerate(fields):
            ttk.Label(form, text=label).grid(row=0, column=i, sticky="w", padx=3)
            widget.grid(row=1, column=i, padx=3, pady=3, sticky="w")
        ttk.Button(form, text="Save Transaction", command=self.on_add_transaction).grid(row=1, column=5, padx=8)
        filters = ttk.LabelFrame(self.transactions_tab, text="Search / filter", padding=8)
        filters.pack(fill="x", pady=8)
        self.filter_goal = ttk.Combobox(filters, state="readonly", width=22)
        self.filter_type = ttk.Combobox(filters, state="readonly", values=["All", "Deposit", "Withdrawal"], width=12)
        self.filter_type.set("All")
        self.filter_start = tk.StringVar()
        self.filter_end = tk.StringVar()
        for i, (label, widget) in enumerate([
            ("Goal", self.filter_goal), ("Type", self.filter_type),
            ("Start date (optional)", ttk.Entry(filters, textvariable=self.filter_start, width=14)),
            ("End date (optional)", ttk.Entry(filters, textvariable=self.filter_end, width=14)),
        ]):
            ttk.Label(filters, text=label).grid(row=0, column=i, sticky="w", padx=3)
            widget.grid(row=1, column=i, padx=3, pady=3, sticky="w")
        ttk.Button(filters, text="Apply Filters", command=self.refresh_transactions).grid(row=1, column=4, padx=5)
        ttk.Button(filters, text="Clear", command=self.clear_filters).grid(row=1, column=5, padx=5)
        columns = ("date", "goal_name", "transaction_type", "amount", "note", "transaction_id")
        self.tx_tree = ttk.Treeview(self.transactions_tab, columns=columns, show="headings", height=13)
        headings = {"date":"Date", "goal_name":"Goal", "transaction_type":"Type", "amount":"Amount (₹)", "note":"Note", "transaction_id":"Transaction ID"}
        widths = {"date":100, "goal_name":170, "transaction_type":110, "amount":120, "note":220, "transaction_id":120}
        for col in columns:
            self.tx_tree.heading(col, text=headings[col])
            self.tx_tree.column(col, width=widths[col], anchor="w")
        self.tx_tree.pack(fill="both", expand=True)
        ttk.Button(self.transactions_tab, text="Delete Selected Transaction", command=self.on_delete_transaction).pack(anchor="e", pady=6)

    def _build_reports(self):
        ttk.Label(self.reports_tab, text="Create visual reports from saved transaction data.",
                  font=("Arial", 12)).pack(anchor="w", pady=(0, 12))
        ttk.Button(self.reports_tab, text="Monthly Deposits vs Withdrawals (Bar Chart)",
                   command=lambda: self._report(show_monthly_chart)).pack(anchor="w", pady=5)
        ttk.Button(self.reports_tab, text="Savings Growth Over Time (Line Chart)",
                   command=lambda: self._report(show_growth_chart)).pack(anchor="w", pady=5)
        ttk.Label(self.reports_tab, text="Reports use the selected dashboard goal when one is selected; otherwise they show all goals.",
                  wraplength=800).pack(anchor="w", pady=12)

    def _report(self, fn):
        try:
            goal_id = self._selected_goal_id()
            fn(goal_id)
        except Exception as exc:
            messagebox.showerror("Report unavailable", str(exc))

    def _selected_goal_id(self):
        value = self.goal_pick.get()
        if not value:
            return ""
        return value.split(" | ", 1)[0]

    def on_add_goal(self):
        try:
            create_goal(self.goal_name.get(), self.goal_target.get(), self.goal_date.get())
            self.goal_name.set("")
            self.goal_target.set("")
            messagebox.showinfo("Saved", "Savings goal created.")
            self.refresh_all()
        except (ValueError, OSError) as exc:
            messagebox.showerror("Invalid goal", str(exc))

    def on_add_transaction(self):
        try:
            selected = self.tx_goal.get()
            if not selected:
                raise ValueError("Create/select a goal first.")
            goal_id = selected.split(" | ", 1)[0]
            add_transaction(goal_id, self.tx_date.get(), self.tx_type.get(),
                            self.tx_amount.get(), self.tx_note.get())
            self.tx_amount.set("")
            self.tx_note.set("")
            messagebox.showinfo("Saved", "Transaction saved.")
            self.refresh_all()
        except (ValueError, OSError) as exc:
            messagebox.showerror("Invalid transaction", str(exc))

    def on_delete_transaction(self):
        selected = self.tx_tree.selection()
        if not selected:
            messagebox.showwarning("Select a transaction", "Select a transaction row first.")
            return
        values = self.tx_tree.item(selected[0], "values")
        if messagebox.askyesno("Confirm deletion", "Delete this transaction permanently?"):
            try:
                delete_transaction(values[-1])
                self.refresh_all()
            except (ValueError, OSError) as exc:
                messagebox.showerror("Could not delete", str(exc))

    def clear_filters(self):
        self.filter_goal.set("")
        self.filter_type.set("All")
        self.filter_start.set("")
        self.filter_end.set("")
        self.refresh_transactions()

    def refresh_all(self):
        try:
            goals = load_goals()
            options = [f"{r.goal_id} | {r['name']}" for _, r in goals.iterrows()]
            for combo in [self.goal_pick, self.tx_goal, self.filter_goal]:
                current = combo.get()
                combo["values"] = options
                if current in options:
                    combo.set(current)
                elif options:
                    combo.set(options[0])
                else:
                    combo.set("")
            self.update_summary()
            self.refresh_transactions()
        except Exception as exc:
            messagebox.showerror("Data error", str(exc))

    def update_summary(self):
        self.summary_text.configure(state="normal")
        self.summary_text.delete("1.0", "end")
        try:
            goal_id = self._selected_goal_id()
            if not goal_id:
                self.summary_text.insert("end", "No goals yet. Open Savings Goals to create your first target.\n")
            else:
                s = goal_summary(goal_id)
                months = f"{s['months']} month(s)" if s["months"] is not None else "Not enough positive saving history"
                lines = [
                    f"Goal: {s['name']}",
                    f"Target amount: ₹{s['target']:,.2f}",
                    f"Total deposits: ₹{s['deposits']:,.2f}",
                    f"Total withdrawals: ₹{s['withdrawals']:,.2f}",
                    f"Current net savings: ₹{s['net']:,.2f}",
                    f"Progress: {s['progress']:.1f}%",
                    f"Amount remaining: ₹{s['remaining']:,.2f}",
                    f"Average positive monthly net-saving pace: ₹{s['pace']:,.2f}",
                    f"Estimated time to target: {months}",
                    f"Target date: {s['target_date']}",
                ]
                self.summary_text.insert("end", "\n".join(lines))
        except Exception as exc:
            self.summary_text.insert("end", f"Could not calculate summary: {exc}")
        self.summary_text.configure(state="disabled")

    def refresh_transactions(self):
        if not hasattr(self, "tx_tree"):
            return
        for item in self.tx_tree.get_children():
            self.tx_tree.delete(item)
        try:
            selected = self.filter_goal.get()
            goal_id = selected.split(" | ", 1)[0] if selected else ""
            start, end = self.filter_start.get().strip(), self.filter_end.get().strip()
            for label, value in [("Start date", start), ("End date", end)]:
                if value:
                    pd.to_datetime(value, format="%Y-%m-%d", errors="raise")
            if start and end and start > end:
                raise ValueError("Start date cannot be later than end date.")
            df = filter_transactions(goal_id, self.filter_type.get() or "All", start, end)
            for _, row in df.iterrows():
                self.tx_tree.insert("", "end", values=(
                    row["date"].strftime("%Y-%m-%d") if pd.notna(row["date"]) else "",
                    row["goal_name"], row["transaction_type"], f"{float(row['amount']):,.2f}",
                    row["note"], row["transaction_id"]))
        except Exception as exc:
            messagebox.showerror("Filter error", str(exc))
