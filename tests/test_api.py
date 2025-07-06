import pytest
import json
import io
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from decimal import Decimal
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import app
from models.receipt import ReceiptData, ProcessingResult

class TestAPI:
    """Test cases for FastAPI endpoints"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.client = TestClient(app)
    
    def test_root_endpoint(self):
        """Test root endpoint returns correct response"""
        response = self.client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "Receipt OCR App API"}
    
    def test_get_categories_endpoint(self):
        """Test get categories endpoint"""
        response = self.client.get("/categories")
        assert response.status_code == 200
        
        categories = response.json()
        assert isinstance(categories, dict)
        assert "Food & Dining" in categories
        assert "Transportation" in categories
        assert "Shopping" in categories
        
        # Check structure of each category
        for category, config in categories.items():
            assert "keywords" in config
            assert "merchants" in config
            assert isinstance(config["keywords"], list)
            assert isinstance(config["merchants"], list)
    
    @patch('services.ocr_service.OCRService.extract_receipt_data')
    def test_upload_single_receipt_success(self, mock_extract):
        """Test successful upload of single receipt"""
        # Mock OCR service response
        mock_receipt_data = ReceiptData(
            date=datetime(2024, 1, 15),
            merchant="Test Store",
            category="Shopping",
            amount=Decimal("25.50"),
            currency="USD"
        )
        mock_extract.return_value = mock_receipt_data
        
        # Create test file
        test_file = io.BytesIO(b"fake image content")
        
        response = self.client.post(
            "/upload",
            files={"files": ("receipt.jpg", test_file, "image/jpeg")}
        )
        
        assert response.status_code == 200
        results = response.json()
        assert len(results) == 1
        assert results[0]["filename"] == "receipt.jpg"
        assert results[0]["status"] == "success"
        assert results[0]["data"]["merchant"] == "Test Store"
        assert results[0]["data"]["category"] == "Shopping"
    
    @patch('services.ocr_service.OCRService.extract_receipt_data')
    def test_upload_multiple_receipts_success(self, mock_extract):
        """Test successful upload of multiple receipts"""
        # Mock OCR service responses
        mock_receipt_data1 = ReceiptData(merchant="Store 1", amount=Decimal("10.00"))
        mock_receipt_data2 = ReceiptData(merchant="Store 2", amount=Decimal("20.00"))
        mock_extract.side_effect = [mock_receipt_data1, mock_receipt_data2]
        
        # Create test files
        test_file1 = io.BytesIO(b"fake image content 1")
        test_file2 = io.BytesIO(b"fake image content 2")
        
        response = self.client.post(
            "/upload",
            files=[
                ("files", ("receipt1.jpg", test_file1, "image/jpeg")),
                ("files", ("receipt2.png", test_file2, "image/png"))
            ]
        )
        
        assert response.status_code == 200
        results = response.json()
        assert len(results) == 2
        assert results[0]["filename"] == "receipt1.jpg"
        assert results[1]["filename"] == "receipt2.png"
        assert all(result["status"] == "success" for result in results)
    
    def test_upload_invalid_file_type(self):
        """Test upload with invalid file type"""
        test_file = io.BytesIO(b"fake content")
        
        response = self.client.post(
            "/upload",
            files={"files": ("document.pdf", test_file, "application/pdf")}
        )
        
        assert response.status_code == 200
        results = response.json()
        assert len(results) == 1
        assert results[0]["filename"] == "document.pdf"
        assert results[0]["status"] == "error"
        assert "Invalid file type" in results[0]["error"]
    
    @patch('services.ocr_service.OCRService.extract_receipt_data')
    def test_upload_ocr_processing_error(self, mock_extract):
        """Test upload with OCR processing error"""
        mock_extract.side_effect = Exception("OCR processing failed")
        
        test_file = io.BytesIO(b"fake image content")
        
        response = self.client.post(
            "/upload",
            files={"files": ("receipt.jpg", test_file, "image/jpeg")}
        )
        
        assert response.status_code == 200
        results = response.json()
        assert len(results) == 1
        assert results[0]["filename"] == "receipt.jpg"
        assert results[0]["status"] == "error"
        assert "OCR processing failed" in results[0]["error"]
    
    def test_upload_no_files(self):
        """Test upload endpoint with no files"""
        response = self.client.post("/upload")
        assert response.status_code == 422  # Unprocessable Entity
    
    @patch('services.export_service.ExportService.export_to_csv')
    def test_export_csv_endpoint(self, mock_export):
        """Test CSV export endpoint"""
        mock_export.return_value = Mock()
        
        test_receipts = [
            {
                "date": "2024-01-15T00:00:00",
                "merchant": "Test Store",
                "category": "Shopping",
                "amount": "25.50",
                "currency": "USD",
                "items": ["Item 1", "Item 2"],
                "raw_text": "Receipt text",
                "confidence": 0.95
            }
        ]
        
        response = self.client.post(
            "/export/csv",
            json={"receipts": test_receipts}
        )
        
        assert response.status_code == 200
        mock_export.assert_called_once()
    
    @patch('services.export_service.ExportService.export_to_excel')
    def test_export_excel_endpoint(self, mock_export):
        """Test Excel export endpoint"""
        mock_export.return_value = Mock()
        
        test_receipts = [
            {
                "date": "2024-01-15T00:00:00",
                "merchant": "Test Store",
                "category": "Shopping",
                "amount": "25.50",
                "currency": "USD",
                "items": ["Item 1"],
                "raw_text": "Receipt text",
                "confidence": 0.95
            }
        ]
        
        response = self.client.post(
            "/export/excel",
            json={"receipts": test_receipts}
        )
        
        assert response.status_code == 200
        mock_export.assert_called_once()
    
    @patch('services.export_service.ExportService.get_summary_stats')
    def test_summary_endpoint(self, mock_summary):
        """Test summary statistics endpoint"""
        mock_summary.return_value = {
            "total_receipts": 2,
            "total_amount": 45.50,
            "categories": {"Shopping": 1, "Food & Dining": 1},
            "currencies": {"USD": 45.50}
        }
        
        test_receipts = [
            {
                "date": "2024-01-15T00:00:00",
                "merchant": "Test Store",
                "category": "Shopping",
                "amount": "25.50",
                "currency": "USD",
                "items": [],
                "raw_text": None,
                "confidence": None
            },
            {
                "date": "2024-01-16T00:00:00",
                "merchant": "Restaurant",
                "category": "Food & Dining",
                "amount": "20.00",
                "currency": "USD",
                "items": [],
                "raw_text": None,
                "confidence": None
            }
        ]
        
        response = self.client.post(
            "/summary",
            json=test_receipts
        )
        
        assert response.status_code == 200
        summary = response.json()
        assert summary["total_receipts"] == 2
        assert summary["total_amount"] == 45.50
        assert "Shopping" in summary["categories"]
        assert "Food & Dining" in summary["categories"]
    
    def test_cors_headers(self):
        """Test CORS headers are present"""
        response = self.client.options("/")
        assert response.status_code == 200
        
        # Test with actual request
        response = self.client.get("/")
        assert response.status_code == 200
    
    def test_upload_mixed_success_and_error(self):
        """Test upload with mix of successful and failed files"""
        with patch('services.ocr_service.OCRService.extract_receipt_data') as mock_extract:
            # First call succeeds, second fails
            mock_extract.side_effect = [
                ReceiptData(merchant="Success Store", amount=Decimal("10.00")),
                Exception("Processing failed")
            ]
            
            test_file1 = io.BytesIO(b"good image")
            test_file2 = io.BytesIO(b"bad image")
            
            response = self.client.post(
                "/upload",
                files=[
                    ("files", ("good.jpg", test_file1, "image/jpeg")),
                    ("files", ("bad.jpg", test_file2, "image/jpeg"))
                ]
            )
            
            assert response.status_code == 200
            results = response.json()
            assert len(results) == 2
            assert results[0]["status"] == "success"
            assert results[1]["status"] == "error"
    
    def test_api_error_handling(self):
        """Test API error handling for invalid requests"""
        # Test invalid JSON in export
        response = self.client.post(
            "/export/csv",
            json={"invalid": "data"}
        )
        assert response.status_code == 422
        
        # Test invalid JSON in summary
        response = self.client.post(
            "/summary",
            json={"invalid": "data"}
        )
        assert response.status_code == 422