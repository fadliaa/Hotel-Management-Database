"""Pure, unit-tested business logic for hotel billing, date overlap, and input validation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

TAX_RATE = Decimal("0.10")
SERVICE_CHARGE_RATE = Decimal("0.05")


@dataclass(frozen=True)
class BillingBreakdown:
    nights: int
    subtotal: Decimal
    tax: Decimal
    service_charge: Decimal
    total: Decimal


def _money(val: Decimal) -> Decimal:
    return val.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def calculate_booking_charges(
    price_per_night: Decimal | float | str,
    check_in: date,
    check_out: date,
) -> BillingBreakdown:
    """Calculate itemized nights, subtotal, 10% tax, 5% service charge, and total."""
    if check_out <= check_in:
        raise ValueError("Check-out date must be strictly after check-in date.")

    nightly = Decimal(str(price_per_night))
    if nightly <= 0:
        raise ValueError("Price per night must be positive.")

    nights = (check_out - check_in).days
    subtotal = _money(nightly * nights)
    tax = _money(subtotal * TAX_RATE)
    service_charge = _money(subtotal * SERVICE_CHARGE_RATE)
    total = _money(subtotal + tax + service_charge)
    return BillingBreakdown(
        nights=nights,
        subtotal=subtotal,
        tax=tax,
        service_charge=service_charge,
        total=total,
    )


def dates_overlap(
    start_a: date,
    end_a: date,
    start_b: date,
    end_b: date,
) -> bool:
    """Return True if half-open stay intervals [start_a, end_a) and [start_b, end_b) overlap.

    Same-day turnover (end_a == start_b) is intentionally allowed.
    """
    return start_a < end_b and start_b < end_a


def parse_selected_id(listbox_text: str) -> Optional[int]:
    """Safely extract integer entity ID from formatted listbox rows like 'ID: 12 | ...'."""
    if not listbox_text or not listbox_text.startswith("ID:"):
        return None
    raw = listbox_text.split("|", 1)[0].replace("ID:", "").strip()
    return int(raw) if raw.isdigit() else None


def normalize_optional_field(value: str) -> Optional[str]:
    """Convert blank GUI strings to None so SQL UNIQUE nullable columns (e.g. email) work cleanly."""
    cleaned = value.strip()
    return cleaned if cleaned else None


def validate_payment_amount(amount_str: str, remaining_balance: Decimal | float) -> Decimal:
    """Validate payment input is a positive number not exceeding the remaining balance."""
    try:
        amount = _money(Decimal(amount_str.strip()))
    except Exception as exc:
        raise ValueError("Payment amount must be a valid number.") from exc

    remaining = _money(Decimal(str(remaining_balance)))
    if amount <= 0:
        raise ValueError("Payment amount must be greater than zero.")
    if amount > remaining:
        raise ValueError(f"Payment amount (${amount:.2f}) exceeds remaining balance (${remaining:.2f}).")
    return amount
