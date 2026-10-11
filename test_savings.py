"""Basic unit tests for SaveSmart business rules."""
import tempfile
import unittest
from pathlib import Path
import storage
import savings

class SaveSmartTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.old_dir = storage.DATA_DIR
        self.old_goals = storage.GOALS_FILE
        self.old_transactions = storage.TRANSACTIONS_FILE
        storage.DATA_DIR = Path(self.temp.name)
        storage.GOALS_FILE = storage.DATA_DIR / "goals.csv"
        storage.TRANSACTIONS_FILE = storage.DATA_DIR / "transactions.csv"

    def tearDown(self):
        storage.DATA_DIR = self.old_dir
        storage.GOALS_FILE = self.old_goals
        storage.TRANSACTIONS_FILE = self.old_transactions
        self.temp.cleanup()

    def test_goal_creation_and_transaction(self):
        goal = savings.create_goal("Laptop", "50000", "2027-12-31")
        tx = savings.add_transaction(goal["goal_id"], "2026-10-11", "Deposit", "1500", "first deposit")
        self.assertEqual(tx["transaction_type"], "Deposit")
        self.assertEqual(float(tx["amount"]), 1500.0)

    def test_invalid_amount(self):
        with self.assertRaises(ValueError):
            savings.create_goal("Laptop", "-1", "2027-12-31")

    def test_invalid_date(self):
        with self.assertRaises(ValueError):
            savings.create_goal("Laptop", "50000", "31-12-2027")

if __name__ == "__main__":
    unittest.main()
