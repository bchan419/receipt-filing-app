from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class ReceiptData(BaseModel):
    """Data model for extracted receipt information"""
    date: Optional[datetime] = None
    merchant: Optional[str] = None
    category: Optional[str] = None
    amount: Optional[Decimal] = None
    currency: Optional[str] = None
    items: Optional[List[str]] = []
    raw_text: Optional[str] = None
    confidence: Optional[float] = None

class ProcessingResult(BaseModel):
    """Result of receipt processing"""
    filename: str
    status: str  # "success" or "error"
    data: Optional[ReceiptData] = None
    error: Optional[str] = None

class ExportRequest(BaseModel):
    """Request model for exporting receipts"""
    receipts: List[ReceiptData]
    format: str = Field(default="csv", description="Export format: csv, xlsx")
    filename: Optional[str] = None