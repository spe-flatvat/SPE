"""Annual government ledger. Amounts are nominal trillion JPY, None is unknown."""
from dataclasses import dataclass, replace
from math import isclose, isfinite

SECTORS = ("CENTRAL", "LOCAL", "SOCIAL_SECURITY")
EXTERNAL = "OUTSIDE_GENERAL_GOVERNMENT"
CATEGORIES = (
    "income_tax", "corporate_tax", "consumption_tax", "other_tax",
    "social_contributions", "other_revenue", "cash_benefits", "medical",
    "education", "other_consumption", "capital_formation", "other_primary_expense",
    "transfer", "interest", "issuance", "redemption", "acquisition",
    "disposal", "internal_stock",
)
PRIMARY_RECEIPTS = CATEGORIES[:6]
PRIMARY_PAYMENTS = CATEGORIES[6:12]
INTERNAL = {"transfer", "interest", "internal_stock"}


def total(*values):
    return sum(values) if all(value is not None for value in values) else None


def scale(value, coefficient):
    return None if value is None else value * coefficient


@dataclass(frozen=True)
class Entry:
    id: str
    year: int
    holder: str
    category: str
    counterparty: str
    side: str
    amount: float | None
    source: str
    coverage: str
    state: str = "identified"
    unit: str = "JPY_TRILLION_NOMINAL"

    def __post_init__(self):
        if (self.holder not in SECTORS or self.category not in CATEGORIES
                or self.counterparty not in (*SECTORS, EXTERNAL, "UNASSIGNED")
                or self.counterparty == self.holder or self.side not in ("in", "out")
                or self.unit != "JPY_TRILLION_NOMINAL" or not self.id or not self.source
                or not self.coverage or (self.amount is not None
                and not isfinite(self.amount))):
            raise ValueError(f"Invalid fiscal entry {self.id}")


def build_ledger(baseline, changes=()):
    """Apply explicit (operation, Entry) pairs against one baseline."""
    entries = {}
    coverage = {}
    for operation, entry in [*(("add", row) for row in baseline), *changes]:
        key = (entry.year, entry.holder, entry.coverage)
        prior = entries.get(entry.id)
        if operation == "add":
            if prior is not None or key in coverage:
                raise ValueError(f"Duplicate fiscal coverage {entry.id}")
            coverage[key] = entry.id
        elif (operation not in ("replace", "delta") or prior is None or coverage.get(key) != entry.id
              or (prior.category, prior.side, prior.counterparty) !=
              (entry.category, entry.side, entry.counterparty)):
            raise ValueError(f"Fiscal change does not match baseline {entry.id}")
        if operation == "delta":
            entry = replace(entry, amount=total(prior.amount, entry.amount))
        if entry.amount is not None and entry.amount < 0:
            raise ValueError(f"Negative resulting fiscal amount {entry.id}")
        entries[entry.id] = entry
    return tuple(entries.values())


def consolidate(entries, year, members=SECTORS):
    """Eliminate matched internal legs and retain unresolved legs in an audit."""
    rows = [r for r in entries if r.year == year and r.holder in members]
    outward = [r for r in rows if r.counterparty not in members]
    pairs = {}
    audit = []
    for r in rows:
        if r.counterparty == "UNASSIGNED":
            audit.append(dict(category=r.category, payer=r.holder, receiver=r.counterparty,
                              status="UNASSIGNED_COUNTERPARTY", unmatched=r.amount))
        if r.counterparty not in members:
            continue
        payer, receiver = (r.holder, r.counterparty) if r.side == "out" else (r.counterparty, r.holder)
        pairs.setdefault((r.category, r.coverage, payer, receiver), {}).setdefault(r.side, []).append(r.amount)
    for (category, coverage, payer, receiver), legs in pairs.items():
        paid = total(*legs["out"]) if "out" in legs else None
        received = total(*legs["in"]) if "in" in legs else None
        matched = (category in INTERNAL and paid is not None and received is not None
                   and isclose(paid, received, rel_tol=0, abs_tol=1e-9))
        unmatched = (0.0 if matched else None if "in" in legs and received is None
                     or "out" in legs and paid is None else (paid or 0) - (received or 0))
        audit.append(dict(category=category, coverage=coverage, payer=payer, receiver=receiver,
                          paid=paid, received=received, eliminated=paid if matched else None,
                          unmatched=unmatched, status="MATCHED" if matched else "UNRESOLVED"))
    return outward, audit


def stock_flow(opening, additions, deductions, adjustment):
    if deductions is None:
        return None
    return total(opening, additions, -deductions, adjustment)


def balances(primary_revenue, primary_expense, interest_paid, interest_received,
             cash_operating_balance=None, cash_inflows=None, cash_outflows=None):
    pb = stock_flow(primary_revenue, 0, primary_expense, 0)
    net_interest = stock_flow(interest_paid, 0, interest_received, 0)
    funding_balance = stock_flow(cash_operating_balance, cash_inflows, cash_outflows, 0)
    return dict(pb=pb, net_interest=net_interest,
                balance=stock_flow(pb, 0, net_interest, 0),
                cash_balance=funding_balance,
                funding_shortfall=max(0, -funding_balance) if funding_balance is not None else None)


def account(entries, year, members, complete=(), cash_operating_balance=None):
    """Calculate only ledger columns whose coverage has been explicitly certified."""
    rows, audit = consolidate(entries, year, members)

    def aggregate(categories, side):
        chosen = [r for r in rows if r.category in categories and r.side == side]
        if (not all((category, side) in complete for category in categories)
                or any(r.side == side and r.counterparty == "UNASSIGNED" for r in chosen)
                or any(r["category"] in categories and r["status"] != "MATCHED" for r in audit)):
            return None
        return total(*(r.amount for r in chosen))

    revenue = aggregate((*PRIMARY_RECEIPTS, "transfer"), "in")
    expense = aggregate((*PRIMARY_PAYMENTS, "transfer"), "out")
    received = aggregate(("interest",), "in")
    paid = aggregate(("interest",), "out")
    issuance = aggregate(("issuance",), "in")
    redemption = aggregate(("redemption",), "out")
    acquisitions = aggregate(("acquisition",), "out")
    disposals = aggregate(("disposal",), "in")
    return dict(primary_revenue=revenue, primary_expense=expense,
                revenue=total(revenue, received), expenditure=total(expense, paid),
                interest_paid=paid, interest_received=received,
                issuance=issuance, redemption=redemption,
                asset_acquisitions=acquisitions, asset_disposals=disposals,
                **balances(revenue, expense, paid, received, cash_operating_balance,
                           total(issuance, disposals), total(redemption, acquisitions))), audit


def annual_stocks(opening_debt, issuance, redemption, debt_sfa,
                  opening_assets, acquisitions, disposals, asset_sfa):
    debt = stock_flow(opening_debt, issuance, redemption, debt_sfa)
    assets = stock_flow(opening_assets, acquisitions, disposals, asset_sfa)
    return dict(debt_end=debt, assets_end=assets, net_debt=stock_flow(debt, 0, assets, 0))


def interest_on_opening(opening_debt, borrowing_rate, opening_assets, yield_rate):
    paid = None if opening_debt is None or borrowing_rate is None else opening_debt * borrowing_rate
    received = None if opening_assets is None or yield_rate is None else opening_assets * yield_rate
    return paid, received
