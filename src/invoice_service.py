from dataclasses import dataclass
from typing import List, Optional, Dict, Tuple

@dataclass
class LineItem:
    sku: str
    category: str
    unit_price: float
    qty: int
    fragile: bool = False

@dataclass
class Invoice:
    invoice_id: str
    customer_id: str
    country: str
    membership: str
    coupon: Optional[str]
    items: List[LineItem]

class InvoiceService:
    SHIPPING_RULES = {
        "TH": [(500, 60)],
        "JP": [(4000, 600)],
        "US": [(100, 15), (300, 8)],
        "DEFAULT": [(200, 25)]
    }

    TAX_RATE = {
        "TH": 0.07,
        "JP": 0.10,
        "US": 0.08,
        "DEFAULT": 0.05
    }

    def __init__(self) -> None:
        self._coupon_rate: Dict[str, float] = {
            "WELCOME10": 0.10,
            "VIP20": 0.20,
            "STUDENT5": 0.05
        }

    def _validate(self, inv: Invoice) -> None:
        if not inv or not inv.invoice_id or not inv.customer_id:
            raise ValueError("Invalid invoice header")
        if not inv.items:
            raise ValueError("Invoice must contain items")

        for it in inv.items:
            if not it.sku or it.qty <= 0 or it.unit_price < 0:
                raise ValueError(f"Invalid item {it.sku}")

    def _shipping_cost(self, country: str, subtotal: float) -> float:
        rules = self.SHIPPING_RULES.get(country, self.SHIPPING_RULES["DEFAULT"])
        for limit, cost in rules:
            if subtotal < limit:
                return cost
        return 0.0

    def _tax(self, country: str, amount: float) -> float:
        return amount * self.TAX_RATE.get(country, self.TAX_RATE["DEFAULT"])

    def compute_total(self, inv: Invoice) -> Tuple[float, List[str]]:
        warnings: List[str] = []
        self._validate(inv)

        subtotal = sum(it.unit_price * it.qty for it in inv.items)
        fragile_fee = sum(5.0 * it.qty for it in inv.items if it.fragile)

        discount = 0.0
        if inv.membership == "gold":
            discount = subtotal * 0.03
        elif inv.membership == "platinum":
            discount = subtotal * 0.05
        elif subtotal > 3000:
            discount = 20

        if inv.coupon:
            rate = self._coupon_rate.get(inv.coupon.strip())
            if rate:
                discount += subtotal * rate
            else:
                warnings.append("Unknown coupon")

        shipping = self._shipping_cost(inv.country, subtotal)
        tax = self._tax(inv.country, subtotal - discount)

        total = max(0, subtotal + shipping + fragile_fee + tax - discount)

        if subtotal > 10000 and inv.membership not in ("gold", "platinum"):
            warnings.append("Consider membership upgrade")

        return total, warnings
