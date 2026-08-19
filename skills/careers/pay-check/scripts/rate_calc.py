#!/usr/bin/env python3
"""Pay arithmetic: day rates, annual figures, and employment against contracting.

This script does arithmetic only. It holds no rates for any country, contacts no
network, and has no opinion about anyone's tax position. Every figure is supplied
by the caller, and every result repeats the inputs it used, so any number can be
traced back to the assumption behind it.

Tax is handled by passing a rate file with --rates: thresholds, percentages, caps
and reliefs, each with the source it came from. The caller researches those
parameters; this script applies them. That split is deliberate. Looking up a
published threshold is checkable against a government page in a minute; an
"effective rate of 33%" is somebody's arithmetic and cannot be checked at all.

No country data is stored here, including in the tests, which use a fictional
country. Stored rates go stale silently, and a wrong tax figure presented
confidently is worse than no tax figure.

Subcommands (run each with --help for its options):

  days            billable days from holiday, non-billable days and utilisation
  day-to-annual   a day rate to an annual figure
  annual-to-day   an annual figure to a day rate
  compare         employment against contracting, like for like
  convert         currency conversion at a rate you supply
  rates-template  print the rate file this script expects, for filling in
  selftest        check the arithmetic

Add --json to any subcommand for machine-readable output.
"""

import argparse
import json
import sys

DEFAULT_WORKING_DAYS = 260  # 52 weeks x 5 days, before holiday or anything else


# --- calculations ------------------------------------------------------------

def billable_days(working_days, public_holidays, leave_days,
                  non_billable_days, utilisation):
    """Days actually invoiced, after time off and non-billable time."""
    available = working_days - public_holidays - leave_days - non_billable_days
    billable = available * utilisation
    return {
        "working_days": working_days,
        "public_holidays": public_holidays,
        "leave_days": leave_days,
        "non_billable_days": non_billable_days,
        "utilisation": utilisation,
        "available_days": round(available, 2),
        "billable_days": round(billable, 2),
    }


def day_to_annual(day_rate, days):
    return {"day_rate": day_rate, "billable_days": days,
            "annual": round(day_rate * days, 2)}


def annual_to_day(annual, days):
    if days <= 0:
        raise ValueError("billable days must be greater than zero")
    return {"annual": annual, "billable_days": days,
            "day_rate": round(annual / days, 2)}


def compare(salary, day_rate, days, employer_pension, benefits_value,
            business_costs, own_pension, employee_tax_pct, contractor_tax_pct,
            rates=None):
    """Employment against contracting on a comparable basis.

    Paid leave is not added to the employed side: it is already inside the
    salary. It shows up on the contracting side as fewer billable days.
    """
    if days <= 0:
        raise ValueError("billable days must be greater than zero")

    employed_package = salary + employer_pension + benefits_value
    contract_gross = day_rate * days
    contract_after_costs = contract_gross - business_costs - own_pension

    result = {
        "assumptions": {
            "billable_days": days,
            "employer_pension": employer_pension,
            "benefits_value": benefits_value,
            "business_costs": business_costs,
            "own_pension": own_pension,
            "tax_basis": "none",
        },
        "employment": {
            "salary": salary,
            "package": round(employed_package, 2),
            "equivalent_day_rate": round(employed_package / days, 2),
        },
        "contracting": {
            "day_rate": day_rate,
            "gross": round(contract_gross, 2),
            "after_costs": round(contract_after_costs, 2),
        },
    }

    if rates:
        emp = employment_tax(salary, rates)
        sef = self_employed_tax(contract_gross, business_costs + own_pension, rates)
        result["assumptions"].update({
            "tax_basis": "rate file",
            "country": rates.get("country", ""),
            "tax_year": rates.get("tax_year", ""),
            "sources": rates.get("sources", []),
            "notes": rates.get("notes", ""),
        })
        result["employment"]["tax"] = emp
        result["contracting"]["tax"] = sef
        # benefits and employer pension are added after tax here: they are not
        # cash the person is taxed on in this model. Say so rather than hide it.
        employed_net = emp["net"] + employer_pension + benefits_value
        contract_net = sef["net"]
        result["employment"]["after_tax"] = round(employed_net, 2)
        result["contracting"]["after_tax"] = round(contract_net, 2)
        a, b = employed_net, contract_net
        match_rate = solve_match_rate(a, days, business_costs, own_pension, rates)

    elif employee_tax_pct is not None and contractor_tax_pct is not None:
        employed_net = employed_package * (1 - employee_tax_pct / 100)
        contract_net = contract_after_costs * (1 - contractor_tax_pct / 100)
        result["assumptions"].update({
            "tax_basis": "flat rates supplied by the caller",
            "employee_tax_pct": employee_tax_pct,
            "contractor_tax_pct": contractor_tax_pct,
            "warning": ("flat effective rates ignore brackets, caps and reliefs. "
                        "Pass --rates for a result anyone can check"),
        })
        result["employment"]["after_tax"] = round(employed_net, 2)
        result["contracting"]["after_tax"] = round(contract_net, 2)
        a, b = employed_net, contract_net
        match_rate = (a / (1 - contractor_tax_pct / 100)
                      + business_costs + own_pension) / days

    else:
        a, b = employed_package, contract_after_costs
        match_rate = (a + business_costs + own_pension) / days

    basis = result["assumptions"]["tax_basis"]
    result["comparison"] = {
        "basis": "before tax" if basis == "none" else f"after tax ({basis})",
        "difference": round(b - a, 2),
        "contracting_vs_employment_pct": round((b / a - 1) * 100, 2) if a else None,
        "day_rate_to_match_employment": round(match_rate, 2),
    }
    return result


# --- tax engine -------------------------------------------------------------
# Everything below works from parameters in a rate file. Nothing here knows any
# country's rules; it knows how brackets, caps, floors and credits behave.

RATES_TEMPLATE = {
    "country": "",
    "currency": "",
    "tax_year": 0,
    "sources": ["url of the tax authority page each figure came from"],
    "notes": "anything a reader needs to judge whether these apply to them",
    "employment": {
        "income_tax_bands": [[0, 0.0]],
        "credits": [{"name": "", "amount": 0}],
        "contributions": [{"name": "", "pct": 0.0, "cap": None}],
    },
    "self_employed": {
        "income_tax_bands": [[0, 0.0]],
        "credits": [{"name": "", "amount": 0}],
        "expense_allowance": {"pct": 0.0, "cap": None},
        "contributions": [{"name": "", "pct": 0.0, "base_pct": 100.0,
                           "cap": None, "min_annual": 0}],
    },
    "reliefs": [{
        "name": "",
        "conditions": "who qualifies, and for how long",
        "applies_to": "employment | self_employed | both",
        "exempt_income": 0,
    }],
}


def tax_on(amount, bands):
    """Progressive tax. Bands are [lower_threshold, percent], lowest first."""
    if amount <= 0 or not bands:
        return 0.0
    bands = sorted(bands, key=lambda b: b[0])
    total = 0.0
    for i, (floor, pct) in enumerate(bands):
        if amount <= floor:
            break
        ceiling = bands[i + 1][0] if i + 1 < len(bands) else None
        top = min(amount, ceiling) if ceiling is not None else amount
        total += (top - floor) * pct / 100.0
        # the band above starts where this one ended
    return total


def contributions_on(base, specs):
    """Percentage charges, each with an optional cap and annual minimum."""
    out, total = [], 0.0
    for spec in specs or []:
        charge_base = base * (spec.get("base_pct", 100.0) / 100.0)
        cap = spec.get("cap")
        if cap is not None:
            charge_base = min(charge_base, cap)
        amount = charge_base * spec.get("pct", 0.0) / 100.0
        floor = spec.get("min_annual") or 0
        if amount < floor:
            amount = floor
        out.append(f"{spec.get('name', 'contribution')}: "
                   f"{round(amount, 2)} on a base of {round(charge_base, 2)}")
        total += amount
    return round(total, 2), out


def exempt_for(rates, side):
    """Total income exempted by reliefs that apply to this side."""
    total, applied = 0.0, []
    for relief in rates.get("reliefs") or []:
        scope = relief.get("applies_to", "both")
        if scope not in (side, "both"):
            continue
        amount = relief.get("exempt_income") or 0
        if amount:
            total += amount
            applied.append(relief.get("name", "relief"))
    return total, applied


def employment_tax(gross, rates):
    side = rates.get("employment") or {}
    contributions, breakdown = contributions_on(gross, side.get("contributions"))
    exempt, applied = exempt_for(rates, "employment")
    taxable = max(0.0, gross - exempt)
    tax = tax_on(taxable, side.get("income_tax_bands"))
    credits = sum(c.get("amount", 0) for c in side.get("credits") or [])
    tax = max(0.0, tax - credits)
    return {
        "gross": round(gross, 2),
        "exempt_income": round(exempt, 2),
        "reliefs_applied": applied,
        "taxable": round(taxable, 2),
        "income_tax_after_credits": round(tax, 2),
        "credits": round(credits, 2),
        "contributions": contributions,
        "contribution_detail": breakdown,
        "net": round(gross - contributions - tax, 2),
    }


def self_employed_tax(gross, actual_costs, rates):
    side = rates.get("self_employed") or {}
    allowance = side.get("expense_allowance") or {}
    if allowance.get("pct"):
        deduction = gross * allowance["pct"] / 100.0
        if allowance.get("cap") is not None:
            deduction = min(deduction, allowance["cap"])
        basis = "expense allowance"
    else:
        deduction = actual_costs
        basis = "actual costs"

    profit = max(0.0, gross - deduction)
    contributions, breakdown = contributions_on(profit, side.get("contributions"))
    exempt, applied = exempt_for(rates, "self_employed")
    taxable = max(0.0, profit - exempt)
    tax = tax_on(taxable, side.get("income_tax_bands"))
    credits = sum(c.get("amount", 0) for c in side.get("credits") or [])
    tax = max(0.0, tax - credits)
    return {
        "gross": round(gross, 2),
        "deduction_basis": basis,
        "deduction": round(deduction, 2),
        "taxable_profit": round(profit, 2),
        "exempt_income": round(exempt, 2),
        "reliefs_applied": applied,
        "taxable": round(taxable, 2),
        "income_tax_after_credits": round(tax, 2),
        "credits": round(credits, 2),
        "contributions": contributions,
        "contribution_detail": breakdown,
        # actual costs leave the bank account whether or not they were deductible
        "net": round(gross - actual_costs - contributions - tax, 2),
    }


def solve_match_rate(target_net, days, business_costs, own_pension, rates,
                     iterations=60):
    """The day rate whose after-tax result equals target_net.

    Solved by bisection rather than by scaling a take-home ratio. Under
    progressive tax the ratio changes as income does, so scaling gives a rate
    that is wrong by more the further it moves -- and this is the number someone
    actually decides on.
    """
    low, high = 0.0, max(target_net, 1.0) * 10 / max(days, 1)
    costs = business_costs + own_pension
    for _ in range(iterations):
        mid = (low + high) / 2
        net = self_employed_tax(mid * days, costs, rates)["net"]
        if net < target_net:
            low = mid
        else:
            high = mid
    return (low + high) / 2


def convert(amount, from_ccy, to_ccy, rate):
    return {"amount": amount, "from": from_ccy.upper(), "to": to_ccy.upper(),
            "rate": rate, "converted": round(amount * rate, 2),
            "note": f"1 {from_ccy.upper()} = {rate} {to_ccy.upper()}, rate supplied by caller"}


# --- output -----------------------------------------------------------------

def emit(data, as_json):
    if as_json:
        print(json.dumps(data, indent=2))
        return
    _print_block(data, 0)


def _print_block(data, indent):
    pad = " " * indent
    for key, value in data.items():
        label = key.replace("_", " ")
        if isinstance(value, dict):
            print(f"{pad}{label}:")
            _print_block(value, indent + 2)
        elif isinstance(value, list):
            if not value:
                continue
            print(f"{pad}{label}:")
            for item in value:
                if isinstance(item, dict):
                    _print_block(item, indent + 2)
                else:
                    print(f"{pad}  {item}")
        else:
            print(f"{pad}{label}: {value}")


# --- selftest ---------------------------------------------------------------

def selftest():
    checks = []

    d = billable_days(260, 10, 25, 5, 1.0)
    checks.append(("available days after 40 days off", d["available_days"], 220.0))
    checks.append(("billable at full utilisation", d["billable_days"], 220.0))

    d = billable_days(260, 0, 0, 0, 0.8)
    checks.append(("utilisation applied", d["billable_days"], 208.0))

    checks.append(("day rate to annual", day_to_annual(800, 220)["annual"], 176000))
    checks.append(("annual to day rate", annual_to_day(176000, 220)["day_rate"], 800.0))

    c = compare(salary=100000, day_rate=800, days=220, employer_pension=5000,
                benefits_value=2000, business_costs=6000, own_pension=0,
                employee_tax_pct=None, contractor_tax_pct=None)
    checks.append(("employed package", c["employment"]["package"], 107000))
    checks.append(("employed equivalent day rate", c["employment"]["equivalent_day_rate"], 486.36))
    checks.append(("contract after costs", c["contracting"]["after_costs"], 170000))
    checks.append(("day rate to match employment", c["comparison"]["day_rate_to_match_employment"], 513.64))

    checks.append(("currency conversion", convert(1000, "eur", "czk", 25.3)["converted"], 25300.0))

    # A fictional country, so no real rates are stored anywhere in this
    # repository -- including here, where they would look authoritative.
    rates = {
        "country": "Exampleland", "tax_year": 2026, "sources": ["fictional"],
        "employment": {
            "income_tax_bands": [[0, 10], [500000, 30]],
            "credits": [{"name": "basic", "amount": 20000}],
            "contributions": [{"name": "social", "pct": 10, "cap": 600000},
                              {"name": "health", "pct": 5}],
        },
        "self_employed": {
            "income_tax_bands": [[0, 10], [500000, 30]],
            "credits": [{"name": "basic", "amount": 20000}],
            "expense_allowance": {"pct": 40, "cap": 300000},
            "contributions": [{"name": "social", "pct": 20, "base_pct": 50,
                               "min_annual": 30000}],
        },
        "reliefs": [{"name": "returning resident", "applies_to": "both",
                     "exempt_income": 100000}],
    }

    checks.append(("progressive bands", tax_on(600000, [[0, 10], [500000, 30]]), 80000.0))
    checks.append(("below the first threshold", tax_on(100000, [[0, 10], [500000, 30]]), 10000.0))
    checks.append(("no income, no tax", tax_on(0, [[0, 10]]), 0.0))

    capped, _ = contributions_on(800000, [{"name": "s", "pct": 10, "cap": 600000}])
    checks.append(("contribution cap applied", capped, 60000.0))
    floored, _ = contributions_on(10000, [{"name": "s", "pct": 20, "min_annual": 30000}])
    checks.append(("contribution floor applied", floored, 30000.0))
    based, _ = contributions_on(700000, [{"name": "s", "pct": 20, "base_pct": 50}])
    checks.append(("contribution base fraction", based, 70000.0))

    e = employment_tax(800000, rates)
    checks.append(("employment contributions", e["contributions"], 100000.0))
    checks.append(("employment tax after credits", e["income_tax_after_credits"], 90000.0))
    checks.append(("employment net", e["net"], 610000.0))

    se = self_employed_tax(1000000, 100000, rates)
    checks.append(("expense allowance capped", se["deduction"], 300000.0))
    checks.append(("self-employed tax after credits", se["income_tax_after_credits"], 60000.0))
    checks.append(("self-employed net, actual costs deducted", se["net"], 770000.0))

    solved = solve_match_rate(610000, 200, 100000, 0, rates)
    landed = self_employed_tax(solved * 200, 100000, rates)["net"]
    checks.append(("solved match rate lands on target", round(landed), 610000))

    failed = 0
    for name, got, want in checks:
        ok = abs(got - want) < 0.011
        if not ok:
            failed += 1
        print(f"{'ok  ' if ok else 'FAIL'} {name}: got {got}, want {want}")
    print(f"\n{len(checks) - failed}/{len(checks)} passed")
    return 1 if failed else 0


# --- cli --------------------------------------------------------------------

def main():
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    def add_json(sp):
        sp.add_argument("--json", action="store_true", help="machine-readable output")

    sp = sub.add_parser("days", help="billable days after time off and utilisation")
    sp.add_argument("--working-days", type=float, default=DEFAULT_WORKING_DAYS,
                    help=f"calendar working days in the year (default {DEFAULT_WORKING_DAYS})")
    sp.add_argument("--public-holidays", type=float, default=0)
    sp.add_argument("--leave-days", type=float, default=0,
                    help="holiday taken, paid or unpaid")
    sp.add_argument("--non-billable-days", type=float, default=0,
                    help="sickness, admin, business development, gaps between contracts")
    sp.add_argument("--utilisation", type=float, default=1.0,
                    help="fraction of available days actually billed, 0-1 (default 1.0)")
    add_json(sp)

    sp = sub.add_parser("day-to-annual", help="day rate to annual figure")
    sp.add_argument("--day-rate", type=float, required=True)
    sp.add_argument("--billable-days", type=float, required=True)
    add_json(sp)

    sp = sub.add_parser("annual-to-day", help="annual figure to day rate")
    sp.add_argument("--annual", type=float, required=True)
    sp.add_argument("--billable-days", type=float, required=True)
    add_json(sp)

    sp = sub.add_parser("compare", help="employment against contracting")
    sp.add_argument("--annual-salary", type=float, required=True)
    sp.add_argument("--day-rate", type=float, required=True)
    sp.add_argument("--billable-days", type=float, required=True,
                    help="use the days subcommand to work this out")
    sp.add_argument("--employer-pension", type=float, default=0,
                    help="employer pension contribution, annual amount")
    sp.add_argument("--benefits-value", type=float, default=0,
                    help="cash value of benefits: insurance, allowances, bonus if reliable")
    sp.add_argument("--business-costs", type=float, default=0,
                    help="accountancy, insurance, equipment, software, annual amount")
    sp.add_argument("--own-pension", type=float, default=0,
                    help="pension the contractor pays themselves, for parity")
    sp.add_argument("--employee-tax-pct", type=float, default=None,
                    help="effective tax rate on employment, percent. Both tax options "
                         "are needed or neither is applied")
    sp.add_argument("--contractor-tax-pct", type=float, default=None,
                    help="effective tax rate on contracting, percent")
    sp.add_argument("--rates", default=None,
                    help="JSON rate file: thresholds, contributions and reliefs, "
                         "with the sources they came from. Run rates-template to "
                         "see the shape. Preferred over the flat --*-tax-pct "
                         "options, which cannot express brackets or caps")
    add_json(sp)

    sp = sub.add_parser("convert", help="currency conversion at a rate you supply")
    sp.add_argument("--amount", type=float, required=True)
    sp.add_argument("--from", dest="from_ccy", required=True)
    sp.add_argument("--to", dest="to_ccy", required=True)
    sp.add_argument("--rate", type=float, required=True,
                    help="units of --to per one unit of --from")
    add_json(sp)

    sp = sub.add_parser("rates-template",
                        help="print the rate file this script expects")
    add_json(sp)

    sub.add_parser("selftest", help="check the arithmetic")

    a = p.parse_args()

    try:
        if a.cmd == "selftest":
            return selftest()
        if a.cmd == "rates-template":
            print(json.dumps(RATES_TEMPLATE, indent=2))
            return 0
        if a.cmd == "days":
            out = billable_days(a.working_days, a.public_holidays, a.leave_days,
                                a.non_billable_days, a.utilisation)
        elif a.cmd == "day-to-annual":
            out = day_to_annual(a.day_rate, a.billable_days)
        elif a.cmd == "annual-to-day":
            out = annual_to_day(a.annual, a.billable_days)
        elif a.cmd == "compare":
            if (a.employee_tax_pct is None) != (a.contractor_tax_pct is None):
                print("both --employee-tax-pct and --contractor-tax-pct are needed, "
                      "or neither", file=sys.stderr)
                return 2
            rates = None
            if a.rates:
                try:
                    rates = json.load(open(a.rates, encoding="utf-8"))
                except (OSError, ValueError) as error:
                    print(f"cannot read rate file {a.rates}: {error}", file=sys.stderr)
                    return 2
                missing = [f for f in ("country", "tax_year", "sources")
                           if not rates.get(f)]
                if missing:
                    print("rate file is missing " + ", ".join(missing) +
                          ". A tax figure without a year and a source cannot be "
                          "checked by anyone, so it is not produced.",
                          file=sys.stderr)
                    return 2
            out = compare(a.annual_salary, a.day_rate, a.billable_days,
                          a.employer_pension, a.benefits_value, a.business_costs,
                          a.own_pension, a.employee_tax_pct, a.contractor_tax_pct,
                          rates)
        elif a.cmd == "convert":
            out = convert(a.amount, a.from_ccy, a.to_ccy, a.rate)
        else:
            p.error("unknown subcommand")
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    emit(out, a.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
