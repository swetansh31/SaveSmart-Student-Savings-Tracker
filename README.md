# SaveSmart — Student Savings Tracker

A simple Python desktop application for recording student savings, tracking goals, filtering transactions, estimating time to target, and generating charts.

## Features
- Create savings goals with a target amount and target date.
- Record deposits and withdrawals with dates and notes.
- Store data persistently in CSV files.
- Calculate total deposits, withdrawals, net savings, progress percentage, remaining amount, and estimated months to target.
- Search/filter transactions by goal, type, and date range.
- Generate monthly deposits-vs-withdrawals bar chart and cumulative savings growth line chart.
- Validate user input and show helpful error messages.

## Requirements
- Python 3.10 or newer recommended
- Tkinter (usually included with standard Python on Windows)
- Packages listed in `requirements.txt`

## Setup
Open a terminal in the project folder:

```bash
python -m venv .venv
```

Windows:
```bat
.venv\Scripts\activate
```

macOS/Linux:
```bash
source .venv/bin/activate
```

Install dependencies:
```bash
python -m pip install -r requirements.txt
```

## Run
```bash
python main.py
```

CSV data is stored in `data/goals.csv` and `data/transactions.csv`. The files are created when needed.

## Tests
Run from the project root:
```bash
python -m unittest discover -s tests -v
```

## How the estimate works
The app computes monthly net savings (deposits minus withdrawals), averages the months with positive net savings, then divides the remaining goal amount by that pace and rounds up. It is a simple historical estimate and not a guarantee. With no positive saving history, the app reports that there is insufficient history to estimate.

## Module overview
- `main.py`: application entry point
- `gui.py`: Tkinter user interface
- `savings.py`: goal and transaction business rules
- `storage.py`: CSV persistence using Pandas
- `analytics.py`: analysis using Pandas and NumPy
- `reports.py`: Matplotlib charts
- `tests/test_savings.py`: basic automated tests

## Notes
- Amounts must be positive; a withdrawal is entered as a positive amount with transaction type `Withdrawal`.
- Net savings can be negative if withdrawals exceed deposits.
- Progress is displayed between 0% and 100%; net savings and remaining amount are shown separately.
