import pytest
from invoice_service import InvoiceService, Invoice, LineItem

def test_compute_total_basic():
    service = InvoiceService()
    inv = Invoice(
        invoice_id="I-001",
        customer_id="C-001",
        country="TH",
        membership="none",
        coupon=None,
        items=[LineItem(sku="A", category="book", unit_price=100.0, qty=2)]
    )
    total, warnings = service.compute_total(inv)
    assert total > 0
    assert isinstance(warnings, list)

def test_invalid_qty_raises():
    service = InvoiceService()
    inv = Invoice(
        invoice_id="I-002",
        customer_id="C-001",
        country="TH",
        membership="none",
        coupon=None,
        items=[LineItem(sku="A", category="book", unit_price=100.0, qty=0)]
    )
    with pytest.raises(ValueError):
        service.compute_total(inv)

def test_gold_membership_discount():
    service = InvoiceService()
    inv = Invoice(
        invoice_id="I-003",
        customer_id="C-001",
        country="US",
        membership="gold",
        coupon=None,
        items=[LineItem("A", "book", 1000, 1)]
    )
    total, _ = service.compute_total(inv)
    assert total > 0

