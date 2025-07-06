import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from decimal import Decimal

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from services.ocr_service import OCRService
from models.receipt import ReceiptData

class TestOCRService:
    """Test cases for OCRService class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        with patch('services.ocr_service.vision.ImageAnnotatorClient'):
            self.ocr_service = OCRService()
    
    def test_initialization(self):
        """Test OCRService initialization"""
        with patch('services.ocr_service.vision.ImageAnnotatorClient') as mock_client:
            service = OCRService()
            assert service.client is not None
            mock_client.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('services.ocr_service.vision.ImageAnnotatorClient')
    async def test_extract_receipt_data_success(self, mock_client):
        """Test successful receipt data extraction"""
        # Mock Vision API response
        mock_response = Mock()
        mock_response.error.message = ""
        mock_response.text_annotations = [
            Mock(description="TEST STORE\n2024-01-15\nTotal: $25.50\nFood items")
        ]
        
        mock_client_instance = Mock()
        mock_client_instance.text_detection.return_value = mock_response
        mock_client.return_value = mock_client_instance
        
        service = OCRService()
        result = await service.extract_receipt_data(b"fake_image_content")
        
        assert isinstance(result, ReceiptData)
        assert result.raw_text == "TEST STORE\n2024-01-15\nTotal: $25.50\nFood items"
        mock_client_instance.text_detection.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('services.ocr_service.vision.ImageAnnotatorClient')
    async def test_extract_receipt_data_api_error(self, mock_client):
        """Test OCR service with API error"""
        # Mock Vision API error response
        mock_response = Mock()
        mock_response.error.message = "API Error occurred"
        
        mock_client_instance = Mock()
        mock_client_instance.text_detection.return_value = mock_response
        mock_client.return_value = mock_client_instance
        
        service = OCRService()
        
        with pytest.raises(Exception, match="Vision API error: API Error occurred"):
            await service.extract_receipt_data(b"fake_image_content")
    
    @pytest.mark.asyncio
    @patch('services.ocr_service.vision.ImageAnnotatorClient')
    async def test_extract_receipt_data_no_text(self, mock_client):
        """Test OCR service with no text detected"""
        # Mock Vision API response with no text
        mock_response = Mock()
        mock_response.error.message = ""
        mock_response.text_annotations = []
        
        mock_client_instance = Mock()
        mock_client_instance.text_detection.return_value = mock_response
        mock_client.return_value = mock_client_instance
        
        service = OCRService()
        result = await service.extract_receipt_data(b"fake_image_content")
        
        assert isinstance(result, ReceiptData)
        assert result.raw_text == ""
    
    def test_extract_date_various_formats(self):
        """Test date extraction with various formats"""
        with patch('services.ocr_service.vision.ImageAnnotatorClient'):
            service = OCRService()
            
            # Test different date formats
            test_cases = [
                ("Receipt from 2024-01-15", datetime(2024, 1, 15)),
                ("Date: 2024/01/15", datetime(2024, 1, 15)),
                ("15-01-2024 Purchase", datetime(2024, 1, 15)),
                ("01/15/2024 Store", datetime(2024, 1, 15)),
                ("15-01-24 Receipt", datetime(2024, 1, 15)),
                ("01/15/24 Bill", datetime(2024, 1, 15)),
                ("No date here", None),
                ("Invalid date 99/99/99", None)
            ]
            
            for text, expected in test_cases:
                result = service._extract_date(text)
                if expected:
                    assert result == expected, f"Failed for text: {text}"
                else:
                    assert result is None, f"Expected None for text: {text}"
    
    def test_extract_merchant_from_text(self):
        """Test merchant extraction from receipt text"""
        with patch('services.ocr_service.vision.ImageAnnotatorClient'):
            service = OCRService()
            
            test_cases = [
                ("WALMART STORE\n2024-01-15\nTotal: $25.50", "WALMART STORE"),
                ("McDonald's\nReceipt #123\nDate: 2024-01-15", "McDonald's"),
                ("7-ELEVEN\nConvenience Store\n2024-01-15", "7-ELEVEN"),
                ("Receipt\nDate: 2024-01-15\nTotal: $10", None),  # No clear merchant
                ("", None),
                ("2024-01-15\nTotal: $5.00", None)  # Date first, no merchant
            ]
            
            for text, expected in test_cases:
                result = service._extract_merchant(text)
                if expected:
                    assert result == expected, f"Failed for text: {text}"
                else:
                    assert result is None, f"Expected None for text: {text}"
    
    def test_extract_amount_and_currency(self):
        """Test amount and currency extraction"""
        with patch('services.ocr_service.vision.ImageAnnotatorClient'):
            service = OCRService()
            
            test_cases = [
                ("Total: $25.50", {'amount': Decimal("25.50"), 'currency': 'USD'}),
                ("Amount: NT$100", {'amount': Decimal("100"), 'currency': 'NTD'}),
                ("Total: HK$75.25", {'amount': Decimal("75.25"), 'currency': 'HKD'}),
                ("合計: NT$150", {'amount': Decimal("150"), 'currency': 'NTD'}),
                ("總計: 200元", {'amount': Decimal("200"), 'currency': 'NTD'}),
                ("Sum: US$99.99", {'amount': Decimal("99.99"), 'currency': 'USD'}),
                ("Price: $1,234.56", {'amount': Decimal("1234.56"), 'currency': 'USD'}),
                ("No amount here", {}),
                ("Invalid: $abc", {})
            ]
            
            for text, expected in test_cases:
                result = service._extract_amount_and_currency(text)
                if expected:
                    assert result['amount'] == expected['amount'], f"Amount failed for: {text}"
                    assert result['currency'] == expected['currency'], f"Currency failed for: {text}"
                else:
                    assert result == {}, f"Expected empty dict for: {text}"
    
    def test_extract_items_from_text(self):
        """Test item extraction from receipt text"""
        with patch('services.ocr_service.vision.ImageAnnotatorClient'):
            service = OCRService()
            
            text = """WALMART STORE
2024-01-15
Milk 2%
Bread Whole Wheat
Bananas
Total: $15.50
合計: $15.50"""
            
            items = service._extract_items(text)
            
            assert isinstance(items, list)
            assert len(items) <= 10  # Limited to 10 items
            assert "Milk 2%" in items
            assert "Bread Whole Wheat" in items
            assert "Bananas" in items
            # Should not include dates, totals, or store names
            assert "2024-01-15" not in items
            assert "Total: $15.50" not in items
    
    def test_extract_items_empty_text(self):
        """Test item extraction with empty text"""
        with patch('services.ocr_service.vision.ImageAnnotatorClient'):
            service = OCRService()
            
            items = service._extract_items("")
            assert items == []
    
    def test_extract_items_no_valid_items(self):
        """Test item extraction with no valid items"""
        with patch('services.ocr_service.vision.ImageAnnotatorClient'):
            service = OCRService()
            
            text = """2024-01-15
Total: $15.50
合計: $15.50"""
            
            items = service._extract_items(text)
            assert isinstance(items, list)
            # Should have filtered out dates and totals
            assert len([item for item in items if "2024" in item or "Total" in item]) == 0
    
    def test_parse_receipt_text_integration(self):
        """Test complete receipt text parsing"""
        with patch('services.ocr_service.vision.ImageAnnotatorClient'):
            service = OCRService()
            
            text = """STARBUCKS COFFEE
2024-01-15 14:30
Grande Latte
Chocolate Croissant
Subtotal: $8.50
Tax: $0.68
Total: $9.18"""
            
            result = service._parse_receipt_text(text)
            
            assert isinstance(result, ReceiptData)
            assert result.date == datetime(2024, 1, 15)
            assert result.merchant == "STARBUCKS COFFEE"
            assert result.amount == Decimal("9.18")
            assert result.currency == "USD"
            assert "Grande Latte" in result.items
            assert "Chocolate Croissant" in result.items
    
    def test_parse_receipt_text_partial_data(self):
        """Test parsing with partial data"""
        with patch('services.ocr_service.vision.ImageAnnotatorClient'):
            service = OCRService()
            
            text = """Unknown Store
Some item
Another item"""
            
            result = service._parse_receipt_text(text)
            
            assert isinstance(result, ReceiptData)
            assert result.merchant == "Unknown Store"
            assert result.date is None
            assert result.amount is None
            assert result.currency is None
            assert len(result.items) >= 2
    
    def test_parse_receipt_text_chinese_content(self):
        """Test parsing Chinese receipt content"""
        with patch('services.ocr_service.vision.ImageAnnotatorClient'):
            service = OCRService()
            
            text = """台北餐廳
2024-01-15
牛肉麵
珍珠奶茶
合計: NT$250"""
            
            result = service._parse_receipt_text(text)
            
            assert isinstance(result, ReceiptData)
            assert result.merchant == "台北餐廳"
            assert result.date == datetime(2024, 1, 15)
            assert result.amount == Decimal("250")
            assert result.currency == "NTD"
            assert "牛肉麵" in result.items
            assert "珍珠奶茶" in result.items
    
    @pytest.mark.asyncio
    @patch('services.ocr_service.vision.ImageAnnotatorClient')
    async def test_extract_receipt_data_complete_flow(self, mock_client):
        """Test complete receipt data extraction flow"""
        # Mock Vision API response with realistic receipt text
        mock_response = Mock()
        mock_response.error.message = ""
        mock_response.text_annotations = [
            Mock(description="""7-ELEVEN
2024-01-15 10:30
Coffee
Sandwich
Total: $8.50""")
        ]
        
        mock_client_instance = Mock()
        mock_client_instance.text_detection.return_value = mock_response
        mock_client.return_value = mock_client_instance
        
        service = OCRService()
        result = await service.extract_receipt_data(b"fake_image_content")
        
        assert isinstance(result, ReceiptData)
        assert result.merchant == "7-ELEVEN"
        assert result.date == datetime(2024, 1, 15)
        assert result.amount == Decimal("8.50")
        assert result.currency == "USD"
        assert "Coffee" in result.items
        assert "Sandwich" in result.items
        assert "7-ELEVEN" in result.raw_text