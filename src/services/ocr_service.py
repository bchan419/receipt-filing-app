import os
import re
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from google.cloud import vision
import io

from models.receipt import ReceiptData

class OCRService:
    """Service for OCR processing using Google Cloud Vision API"""
    
    def __init__(self):
        self.client = vision.ImageAnnotatorClient()
    
    async def extract_receipt_data(self, image_content: bytes) -> ReceiptData:
        """Extract structured data from receipt image"""
        try:
            # Perform OCR
            raw_text = await self._extract_text(image_content)
            
            # Parse structured data
            parsed_data = self._parse_receipt_text(raw_text)
            parsed_data.raw_text = raw_text
            
            return parsed_data
            
        except Exception as e:
            raise Exception(f"OCR processing failed: {str(e)}")
    
    async def _extract_text(self, image_content: bytes) -> str:
        """Extract text from image using Google Cloud Vision"""
        image = vision.Image(content=image_content)
        response = self.client.text_detection(image=image)
        
        if response.error.message:
            raise Exception(f"Vision API error: {response.error.message}")
        
        texts = response.text_annotations
        if texts:
            return texts[0].description
        return ""
    
    def _parse_receipt_text(self, text: str) -> ReceiptData:
        """Parse receipt text to extract structured data"""
        receipt_data = ReceiptData()
        
        # Extract date
        receipt_data.date = self._extract_date(text)
        
        # Extract merchant
        receipt_data.merchant = self._extract_merchant(text)
        
        # Extract amount and currency
        amount_info = self._extract_amount_and_currency(text)
        receipt_data.amount = amount_info.get('amount')
        receipt_data.currency = amount_info.get('currency')
        
        # Extract items
        receipt_data.items = self._extract_items(text)
        
        return receipt_data
    
    def _extract_date(self, text: str) -> Optional[datetime]:
        """Extract date from receipt text"""
        # Multiple date patterns
        date_patterns = [
            r'\d{4}[-/]\d{1,2}[-/]\d{1,2}',  # YYYY-MM-DD or YYYY/MM/DD
            r'\d{1,2}[-/]\d{1,2}[-/]\d{4}',  # DD-MM-YYYY or MM/DD/YYYY
            r'\d{1,2}[-/]\d{1,2}[-/]\d{2}',  # DD-MM-YY or MM/DD/YY
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    date_str = match.group()
                    # Try different parsing formats
                    for fmt in ['%Y-%m-%d', '%Y/%m/%d', '%d-%m-%Y', '%m/%d/%Y', '%d-%m-%y', '%m/%d/%y']:
                        try:
                            return datetime.strptime(date_str, fmt)
                        except ValueError:
                            continue
                except:
                    continue
        return None
    
    def _extract_merchant(self, text: str) -> Optional[str]:
        """Extract merchant name from receipt text"""
        lines = text.split('\n')
        # Usually merchant name is in the first few lines
        for line in lines[:5]:
            line = line.strip()
            if len(line) > 2 and not re.match(r'^\d+[-/]\d+[-/]\d+', line):
                # Skip obvious non-merchant lines
                skip_words = ['receipt', 'invoice', 'date', 'time', 'total', 'amount', 'tax', 'subtotal', 'sum']
                if not any(word in line.lower() for word in skip_words):
                    # Also skip lines that look like amounts
                    if not re.search(r'\$\d+', line) and not re.search(r'\d+\.\d+', line):
                        return line
        return None
    
    def _extract_amount_and_currency(self, text: str) -> dict:
        """Extract total amount and currency"""
        # Currency patterns for NTD, HKD, USD
        currency_patterns = [
            (r'NT\$?\s*([0-9,]+\.?\d*)', 'NTD'),
            (r'HK\$?\s*([0-9,]+\.?\d*)', 'HKD'),
            (r'US\$?\s*([0-9,]+\.?\d*)', 'USD'),
            (r'\$\s*([0-9,]+\.?\d*)', 'USD'),  # Default $ to USD
            (r'([0-9,]+\.?\d*)\s*元', 'NTD'),   # Chinese Yuan symbol
        ]
        
        # Look for total amount keywords (prioritize "total" over "subtotal")
        total_keywords = ['total', 'amount', 'sum', '合計', '總計', '小計']
        lines = text.split('\n')
        
        # First pass: look for "total" specifically
        for line in lines:
            line_lower = line.lower()
            if 'total' in line_lower and 'subtotal' not in line_lower:
                for pattern, currency in currency_patterns:
                    match = re.search(pattern, line, re.IGNORECASE)
                    if match:
                        amount_str = match.group(1).replace(',', '')
                        try:
                            amount = Decimal(amount_str)
                            return {'amount': amount, 'currency': currency}
                        except:
                            continue
        
        # Second pass: look for other total keywords
        for line in lines:
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in total_keywords):
                for pattern, currency in currency_patterns:
                    match = re.search(pattern, line, re.IGNORECASE)
                    if match:
                        amount_str = match.group(1).replace(',', '')
                        try:
                            amount = Decimal(amount_str)
                            return {'amount': amount, 'currency': currency}
                        except:
                            continue
        
        # If no total found, look for any amount
        for pattern, currency in currency_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    amount = Decimal(amount_str)
                    return {'amount': amount, 'currency': currency}
                except:
                    continue
        
        return {}
    
    def _extract_items(self, text: str) -> List[str]:
        """Extract item list from receipt"""
        lines = text.split('\n')
        items = []
        
        for line in lines:
            line = line.strip()
            # Skip empty lines, dates, totals
            if (len(line) > 2 and 
                not re.match(r'^\d+[-/]\d+[-/]\d+', line) and
                not re.search(r'total|amount|合計|總計', line.lower())):
                items.append(line)
        
        return items[:10]  # Limit to first 10 items