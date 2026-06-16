"""
Optional evaluation scaffold.

Usage idea:
1. Export your Golden Test Set to CSV.
2. Add assistant outputs to a column named assistant_output.
3. Use this script as a starting point to send outputs to an LLM judge.
"""

from pathlib import Path
import pandas as pd

GOLDEN_SET_CSV = Path("golden_test_set.csv")

if __name__ == "__main__":
    if not GOLDEN_SET_CSV.exists():
        print("Place golden_test_set.csv in this folder first.")
        raise SystemExit(1)

    df = pd.read_csv(GOLDEN_SET_CSV)
    required = ["ID", "Category", "Test Case", "Prompt", "Expected Good Output", "Failure Signals", "Quality Criteria", "assistant_output"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        print(f"Missing columns: {missing}")
        raise SystemExit(1)

    print(f"Loaded {len(df)} test cases.")
    print("Next step: call your judge model for each row and store JSON results.")
