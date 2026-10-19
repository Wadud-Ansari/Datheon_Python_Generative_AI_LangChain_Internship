"""Pydantic schemas that define the JSON structure we expect from the LLM."""

from typing import List, Optional

from pydantic import BaseModel, Field


class LineItem(BaseModel):
    description: str = Field(description="What was sold or billed")
    quantity: float = Field(description="Number of units")
    unit_price: float = Field(description="Price per unit")
    total: float = Field(description="quantity x unit_price for this line")


class Invoice(BaseModel):
    invoice_number: Optional[str] = Field(description="Invoice ID or number, null if missing")
    vendor_name: str = Field(description="Company or person issuing the invoice")
    customer_name: Optional[str] = Field(description="Who is being billed, null if missing")
    invoice_date: Optional[str] = Field(description="Issue date in YYYY-MM-DD, null if missing")
    due_date: Optional[str] = Field(description="Payment due date in YYYY-MM-DD, null if missing")
    currency: Optional[str] = Field(description="Currency code such as USD, INR, NPR")
    line_items: List[LineItem] = Field(description="All billed items")
    subtotal: Optional[float] = Field(description="Total before tax, null if missing")
    tax: Optional[float] = Field(description="Tax amount, null if missing")
    total_amount: float = Field(description="Final amount to pay")
