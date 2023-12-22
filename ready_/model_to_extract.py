from typing import Optional
from abc import ABC

from langchain.pydantic_v1 import BaseModel, Field


class Requisites(BaseModel, ABC):
    """Identifying information about invoice in a text for working with WBWorker"""

    invoice_date: str = Field(...)
    customer_name: str = Field(...)
    city: str = Field(...)
    street: str = Field(...)
    state_or_land: Optional[str] = Field(...)
    postal_code: str = Field(...)
    country_code: str = Field(...)
    customer_vat_id: Optional[str] = Field(...)
    order_number: str = Field(...)

    def get_data(self):
        return {
            'A': self.customer_name, 'B': self.customer_vat_id if self.customer_vat_id != "" else None,
            'C': self.street, 'D': self.postal_code,
            'E': self.city + ', ' + self.state_or_land
            if self.state_or_land else self.city,
            'N': self.country_code, 'O': self.order_number,
            'P': self.invoice_date
        }


class ReqModel(BaseModel):

    """Model for working with structured chain"""

    invoice_date: str = Field(..., description="Date of invoice from")
    customer_name: str = Field(..., description="Name of a company or customer")
    city: str = Field(..., description="billing city")
    street: str = Field(..., description="billing street")
    state_or_land: Optional[str] = Field(..., description="state or land")

    postal_code: str = Field(..., description="postal code")
    country_code: str = Field(..., description="Customer Country code of invoice from a text")
    customer_vat_id: Optional[str] = Field(..., description="A value-added tax identification number of "
                                                            "customer in a text")

