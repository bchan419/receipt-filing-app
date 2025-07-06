import pytest
from datetime import datetime
from decimal import Decimal
from pydantic import ValidationError

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from models.receipt import ReceiptData, ProcessingResult, ExportRequest

class TestReceiptData:
    """Test cases for ReceiptData model"""
    
    def test_receipt_data_creation(self):
        """Test creating a valid ReceiptData instance"""
        receipt = ReceiptData(
            date=datetime(2024, 1, 15),
            merchant="Test Store",
            category="Shopping",
            amount=Decimal("25.50"),
            currency="USD",
            items=["Item 1", "Item 2"],
            raw_text="Test receipt text",
            confidence=0.95
        )
        
        assert receipt.date == datetime(2024, 1, 15)
        assert receipt.merchant == "Test Store"
        assert receipt.category == "Shopping"
        assert receipt.amount == Decimal("25.50")
        assert receipt.currency == "USD"
        assert receipt.items == ["Item 1", "Item 2"]
        assert receipt.raw_text == "Test receipt text"
        assert receipt.confidence == 0.95
    
    def test_receipt_data_optional_fields(self):
        """Test ReceiptData with optional fields as None"""
        receipt = ReceiptData()
        
        assert receipt.date is None
        assert receipt.merchant is None
        assert receipt.category is None
        assert receipt.amount is None
        assert receipt.currency is None
        assert receipt.items == []
        assert receipt.raw_text is None
        assert receipt.confidence is None
    
    def test_receipt_data_decimal_amount(self):
        """Test ReceiptData with various decimal amounts"""
        receipt = ReceiptData(amount=Decimal("123.45"))
        assert receipt.amount == Decimal("123.45")
        
        receipt = ReceiptData(amount=Decimal("0.01"))
        assert receipt.amount == Decimal("0.01")
    
    def test_receipt_data_json_serialization(self):
        """Test ReceiptData JSON serialization"""
        receipt = ReceiptData(
            date=datetime(2024, 1, 15),
            merchant="Test Store",
            amount=Decimal("25.50")
        )
        
        # Should be able to convert to dict
        receipt_dict = receipt.model_dump()
        assert receipt_dict['merchant'] == "Test Store"
        assert receipt_dict['amount'] == Decimal("25.50")

class TestProcessingResult:
    """Test cases for ProcessingResult model"""
    
    def test_processing_result_success(self):
        """Test ProcessingResult for successful processing"""
        receipt_data = ReceiptData(merchant="Test Store", amount=Decimal("10.00"))
        result = ProcessingResult(
            filename="test.jpg",
            status="success",
            data=receipt_data
        )
        
        assert result.filename == "test.jpg"
        assert result.status == "success"
        assert result.data == receipt_data
        assert result.error is None
    
    def test_processing_result_error(self):
        """Test ProcessingResult for error case"""
        result = ProcessingResult(
            filename="test.jpg",
            status="error",
            error="OCR processing failed"
        )
        
        assert result.filename == "test.jpg"
        assert result.status == "error"
        assert result.error == "OCR processing failed"
        assert result.data is None
    
    def test_processing_result_required_fields(self):
        """Test ProcessingResult with required fields only"""
        result = ProcessingResult(filename="test.jpg", status="success")
        
        assert result.filename == "test.jpg"
        assert result.status == "success"
        assert result.data is None
        assert result.error is None

class TestExportRequest:
    """Test cases for ExportRequest model"""
    
    def test_export_request_creation(self):
        """Test creating a valid ExportRequest"""
        receipts = [
            ReceiptData(merchant="Store 1", amount=Decimal("10.00")),
            ReceiptData(merchant="Store 2", amount=Decimal("20.00"))
        ]
        
        request = ExportRequest(
            receipts=receipts,
            format="csv",
            filename="export.csv"
        )
        
        assert len(request.receipts) == 2
        assert request.format == "csv"
        assert request.filename == "export.csv"
    
    def test_export_request_default_format(self):
        """Test ExportRequest with default format"""
        receipts = [ReceiptData(merchant="Store 1")]
        request = ExportRequest(receipts=receipts)
        
        assert request.format == "csv"  # Default value
        assert request.filename is None
    
    def test_export_request_empty_receipts(self):
        """Test ExportRequest with empty receipts list"""
        request = ExportRequest(receipts=[])
        
        assert len(request.receipts) == 0
        assert request.format == "csv"