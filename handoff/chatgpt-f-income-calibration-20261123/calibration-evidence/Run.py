"""Validate the transcribed comparison table and derive wage-income shares."""
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load_shares(path):
    shares = []
    with path.open(newline="") as data:
        for rank, row in enumerate(csv.DictReader(data), 1):
            assert int(row["observation_year"]) == 2025 and int(row["quintile"]) == rank
            income = int(row["monthly_income_yen"])
            wage = int(row["monthly_employee_income_yen"])
            assert 0 < wage < income and 0 < float(row["earners"]) <= float(row["persons"])
            upper = int(row["upper_annual_income_yen"]) if row["upper_annual_income_yen"] else float("inf")
            assert not shares or shares[-1][0] < upper
            shares.append((upper, wage/income))
    assert len(shares) == 5 and shares[-1][0] == float("inf")
    return shares


if __name__=="__main__":
    shares = load_shares(HERE/"Wage_Shares.csv")
    print(json.dumps({"checks":16, "failures":0, "wage_shares":[value for _,value in shares]}, indent=2))
