from dataclasses import dataclass
from decimal import Decimal, ROUND_DOWN, ROUND_HALF_UP


CENT = Decimal("0.01")


@dataclass(frozen=True)
class Line:
    unit_price: Decimal
    quantity: int


@dataclass(frozen=True)
class Policy:
    discount_rate: Decimal
    discount_minimum: Decimal
    tax_rate: Decimal
    free_shipping_minimum: Decimal
    shipping_fee: Decimal


def quote(lines: list[Line], policy: Policy) -> dict[str, Decimal]:
    subtotal = sum(
        (line.unit_price * line.quantity for line in lines),
        start=Decimal("0.00"),
    )
    discount = Decimal("0.00")
    if subtotal > policy.discount_minimum:
        discount = (subtotal * policy.discount_rate).quantize(CENT, rounding=ROUND_DOWN)
    merchandise = subtotal - discount
    tax = (subtotal * policy.tax_rate).quantize(CENT, rounding=ROUND_HALF_UP)
    shipping = (
        Decimal("0.00")
        if subtotal >= policy.free_shipping_minimum
        else policy.shipping_fee
    )
    return {
        "subtotal": subtotal,
        "discount": discount,
        "merchandise": merchandise,
        "tax": tax,
        "shipping": shipping,
        "total": merchandise + tax + shipping,
    }
