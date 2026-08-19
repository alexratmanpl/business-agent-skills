#!/usr/bin/env python3
"""Pay arithmetic: day rates, annual figures, and employment against contracting.

This script does arithmetic only. It holds no market data, contacts no network,
and knows nothing about any country's tax system. Every rate, percentage and day
count is supplied by the caller, and every result repeats the inputs it used, so
any figure can be traced back to the assumptions behind it.

Subcommands (run each with --help for its options):

  days            billable days from holiday, non-billable days and utilisation
  day-to-annual   a day rate to an annual figure
  annual-to-day   an annual figure to a day rate
  compare         employment against contracting, like for like
  convert         currency conversion at a rate you supply
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
            business_costs, own_pension, employee_tax_pct, contractor_tax_pct):
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
            "tax_applied": False,
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

    if employee_tax_pct is not None and contractor_tax_pct is not None:
        employed_net = employed_package * (1 - employee_tax_pct / 100)
        contract_net = contract_after_costs * (1 - contractor_tax_pct / 100)
        result["assumptions"]["tax_applied"] = True
        result["assumptions"]["employee_tax_pct"] = employee_tax_pct
        result["assumptions"]["contractor_tax_pct"] = contractor_tax_pct
        result["employment"]["after_tax"] = round(employed_net, 2)
        result["contracting"]["after_tax"] = round(contract_net, 2)
        basis, a, b = "after tax", employed_net, contract_net
    else:
        basis, a, b = "before tax", employed_package, contract_after_costs

    result["comparison"] = {
        "basis": basis,
        "difference": round(b - a, 2),
        "contracting_vs_employment_pct": round((b / a - 1) * 100, 2) if a else None,
        "day_rate_to_match_employment": round(
            (a / (1 - contractor_tax_pct / 100) if basis == "after tax" else a
             ) / days + (business_costs + own_pension) / days, 2),
    }
    return result


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
    add_json(sp)

    sp = sub.add_parser("convert", help="currency conversion at a rate you supply")
    sp.add_argument("--amount", type=float, required=True)
    sp.add_argument("--from", dest="from_ccy", required=True)
    sp.add_argument("--to", dest="to_ccy", required=True)
    sp.add_argument("--rate", type=float, required=True,
                    help="units of --to per one unit of --from")
    add_json(sp)

    sub.add_parser("selftest", help="check the arithmetic")

    a = p.parse_args()

    try:
        if a.cmd == "selftest":
            return selftest()
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
            out = compare(a.annual_salary, a.day_rate, a.billable_days,
                          a.employer_pension, a.benefits_value, a.business_costs,
                          a.own_pension, a.employee_tax_pct, a.contractor_tax_pct)
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
