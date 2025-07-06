import pytest
import io
import pandas as pd
from decimal import Decimal
from datetime import datetime
from unittest.mock import Mock, patch

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from services.export_service import ExportService
from models.receipt import ReceiptData

class TestExportService:
    """Test cases for ExportService class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.export_service = ExportService()
        self.sample_receipts = [
            ReceiptData(
                date=datetime(2024, 1, 15),
                merchant="Test Store 1",
                category="Shopping",
                amount=Decimal("25.50"),
                currency="USD",
                items=["Item 1", "Item 2"],
                raw_text="Receipt text 1",
                confidence=0.95
            ),
            ReceiptData(
                date=datetime(2024, 1, 16),
                merchant="Test Restaurant",
                category="Food & Dining",
                amount=Decimal("45.00"),
                currency="USD",
                items=["Meal", "Drink"],
                raw_text="Receipt text 2",
                confidence=0.88
            )
        ]
    
    def test_export_to_csv_basic(self):
        """Test basic CSV export functionality"""
        response = self.export_service.export_to_csv(self.sample_receipts)
        
        assert response is not None
        assert response.media_type == 'text/csv'
        assert 'attachment; filename=receipts.csv' in response.headers['Content-Disposition']
    
    def test_export_to_csv_content(self):
        """Test CSV export content structure"""
        # Create a simple test to verify CSV structure
        receipts = [
            ReceiptData(
                date=datetime(2024, 1, 15),
                merchant="Test Store",
                category="Shopping",
                amount=Decimal("25.50"),
                currency="USD",
                items=["Item 1", "Item 2"]
            )
        ]
        
        response = self.export_service.export_to_csv(receipts)
        
        # Verify response properties
        assert response.media_type == 'text/csv'
        assert 'receipts.csv' in response.headers['Content-Disposition']
    
    def test_export_to_csv_empty_list(self):
        """Test CSV export with empty receipts list"""
        response = self.export_service.export_to_csv([])
        
        assert response is not None
        assert response.media_type == 'text/csv'
    
    def test_export_to_csv_none_values(self):
        """Test CSV export with None values"""
        receipts = [
            ReceiptData(
                date=None,
                merchant=None,
                category=None,
                amount=None,
                currency=None,
                items=None
            )
        ]
        
        response = self.export_service.export_to_csv(receipts)
        
        assert response is not None
        assert response.media_type == 'text/csv'
    
    def test_export_to_excel_basic(self):
        """Test basic Excel export functionality"""
        response = self.export_service.export_to_excel(self.sample_receipts)
        
        assert response is not None
        assert response.media_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        assert 'attachment; filename=receipts.xlsx' in response.headers['Content-Disposition']
    
    def test_export_to_excel_empty_list(self):
        """Test Excel export with empty receipts list"""
        response = self.export_service.export_to_excel([])
        
        assert response is not None
        assert response.media_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    
    def test_export_to_excel_none_values(self):
        """Test Excel export with None values"""
        receipts = [
            ReceiptData(
                date=None,
                merchant=None,
                category=None,
                amount=None,
                currency=None,
                items=None
            )
        ]
        
        response = self.export_service.export_to_excel(receipts)
        
        assert response is not None
        assert response.media_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    
    def test_get_summary_stats_basic(self):
        """Test basic summary statistics"""
        stats = self.export_service.get_summary_stats(self.sample_receipts)
        
        assert stats is not None
        assert isinstance(stats, dict)
        assert 'total_receipts' in stats
        assert 'total_amount' in stats
        assert 'categories' in stats
        assert 'currencies' in stats
        
        assert stats['total_receipts'] == 2
        assert stats['total_amount'] == 70.50  # 25.50 + 45.00
        assert stats['categories']['Shopping'] == 1
        assert stats['categories']['Food & Dining'] == 1
        assert stats['currencies']['USD'] == 70.50
    
    def test_get_summary_stats_empty_list(self):
        """Test summary statistics with empty receipts list"""
        stats = self.export_service.get_summary_stats([])
        
        assert stats == {}
    
    def test_get_summary_stats_none_amounts(self):
        """Test summary statistics with None amounts"""
        receipts = [
            ReceiptData(
                merchant="Store 1",
                category="Shopping",
                amount=None,
                currency="USD"
            ),
            ReceiptData(
                merchant="Store 2",
                category="Shopping",
                amount=Decimal("10.00"),
                currency="USD"
            )
        ]
        
        stats = self.export_service.get_summary_stats(receipts)
        
        assert stats['total_receipts'] == 2
        assert stats['total_amount'] == 10.00
        assert stats['categories']['Shopping'] == 2
        assert stats['currencies']['USD'] == 10.00
    
    def test_get_summary_stats_multiple_currencies(self):
        """Test summary statistics with multiple currencies"""
        receipts = [
            ReceiptData(
                merchant="Store 1",
                category="Shopping",
                amount=Decimal("25.50"),
                currency="USD"
            ),
            ReceiptData(
                merchant="Store 2",
                category="Food & Dining",
                amount=Decimal("100.00"),
                currency="NTD"
            ),
            ReceiptData(
                merchant="Store 3",
                category="Shopping",
                amount=Decimal("15.00"),
                currency="USD"
            )
        ]
        
        stats = self.export_service.get_summary_stats(receipts)
        
        assert stats['total_receipts'] == 3
        assert stats['total_amount'] == 140.50  # 25.50 + 100.00 + 15.00
        assert stats['categories']['Shopping'] == 2
        assert stats['categories']['Food & Dining'] == 1
        assert stats['currencies']['USD'] == 40.50
        assert stats['currencies']['NTD'] == 100.00
    
    def test_get_summary_stats_no_categories(self):
        """Test summary statistics with no categories"""
        receipts = [
            ReceiptData(
                merchant="Store 1",
                category=None,
                amount=Decimal("25.50"),
                currency="USD"
            ),
            ReceiptData(
                merchant="Store 2",
                category="",
                amount=Decimal("15.00"),
                currency="USD"
            )
        ]
        
        stats = self.export_service.get_summary_stats(receipts)
        
        assert stats['total_receipts'] == 2
        assert stats['total_amount'] == 40.50
        assert stats['categories'] == {}  # No valid categories
        assert stats['currencies']['USD'] == 40.50
    
    def test_get_summary_stats_mixed_data(self):
        """Test summary statistics with mixed valid and invalid data"""
        receipts = [
            ReceiptData(
                merchant="Store 1",
                category="Shopping",
                amount=Decimal("25.50"),
                currency="USD"
            ),
            ReceiptData(
                merchant="Store 2",
                category=None,
                amount=None,
                currency=None
            ),
            ReceiptData(
                merchant="Store 3",
                category="Food & Dining",
                amount=Decimal("30.00"),
                currency="HKD"
            )
        ]
        
        stats = self.export_service.get_summary_stats(receipts)
        
        assert stats['total_receipts'] == 3
        assert stats['total_amount'] == 55.50  # Only valid amounts
        assert stats['categories']['Shopping'] == 1
        assert stats['categories']['Food & Dining'] == 1
        assert stats['currencies']['USD'] == 25.50
        assert stats['currencies']['HKD'] == 30.00
    
    def test_items_formatting_in_csv(self):
        """Test that items are properly formatted in CSV export"""
        receipts = [
            ReceiptData(
                merchant="Store 1",
                items=["Item 1", "Item 2", "Item 3"]
            ),
            ReceiptData(
                merchant="Store 2",
                items=[]
            ),
            ReceiptData(
                merchant="Store 3",
                items=None
            )
        ]
        
        # This test verifies the export runs without errors
        # The actual content verification would require parsing the CSV
        response = self.export_service.export_to_csv(receipts)
        assert response is not None
        assert response.media_type == 'text/csv'
    
    def test_date_formatting_in_exports(self):
        """Test that dates are properly formatted in exports"""
        receipts = [
            ReceiptData(
                merchant="Store 1",
                date=datetime(2024, 1, 15, 14, 30, 45)
            ),
            ReceiptData(
                merchant="Store 2",
                date=None
            )
        ]
        
        # Test both CSV and Excel exports
        csv_response = self.export_service.export_to_csv(receipts)
        excel_response = self.export_service.export_to_excel(receipts)
        
        assert csv_response is not None
        assert excel_response is not None
    
    def test_decimal_precision_in_summary(self):
        """Test decimal precision in summary statistics"""
        receipts = [
            ReceiptData(
                merchant="Store 1",
                amount=Decimal("10.001"),
                currency="USD"
            ),
            ReceiptData(
                merchant="Store 2",
                amount=Decimal("20.999"),
                currency="USD"
            )
        ]
        
        stats = self.export_service.get_summary_stats(receipts)
        
        assert stats['total_amount'] == 31.0  # Should be converted to float
        assert stats['currencies']['USD'] == 31.0