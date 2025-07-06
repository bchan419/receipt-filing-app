import pytest
from decimal import Decimal
from datetime import datetime

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config.categories import CategoryConfig
from models.receipt import ReceiptData

class TestCategoryConfig:
    """Test cases for CategoryConfig class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.category_config = CategoryConfig()
    
    def test_initialization(self):
        """Test CategoryConfig initialization"""
        assert self.category_config.default_categories is not None
        assert self.category_config.custom_categories == {}
        assert 'Food & Dining' in self.category_config.default_categories
        assert 'Transportation' in self.category_config.default_categories
        assert 'Shopping' in self.category_config.default_categories
    
    def test_categorize_by_merchant_keyword(self):
        """Test categorization by merchant name"""
        receipt = ReceiptData(
            merchant="McDonald's Restaurant",
            raw_text="Receipt from McDonald's"
        )
        
        category = self.category_config.categorize_receipt(receipt)
        assert category == "Food & Dining"
    
    def test_categorize_by_text_keyword(self):
        """Test categorization by text content"""
        receipt = ReceiptData(
            merchant="Unknown Store",
            raw_text="Purchase at restaurant for lunch meal"
        )
        
        category = self.category_config.categorize_receipt(receipt)
        assert category == "Food & Dining"
    
    def test_categorize_transportation(self):
        """Test transportation categorization"""
        receipt = ReceiptData(
            merchant="Uber Technologies",
            raw_text="Ride from downtown to airport"
        )
        
        category = self.category_config.categorize_receipt(receipt)
        assert category == "Transportation"
    
    def test_categorize_shopping(self):
        """Test shopping categorization"""
        receipt = ReceiptData(
            merchant="7-Eleven Store",
            raw_text="Convenience store purchase"
        )
        
        category = self.category_config.categorize_receipt(receipt)
        assert category == "Shopping"
    
    def test_categorize_chinese_keywords(self):
        """Test categorization with Chinese keywords"""
        receipt = ReceiptData(
            merchant="台北餐廳",
            raw_text="晚餐消費 餐廳用餐"
        )
        
        category = self.category_config.categorize_receipt(receipt)
        assert category == "Food & Dining"
    
    def test_categorize_utilities(self):
        """Test utilities categorization"""
        receipt = ReceiptData(
            merchant="Taiwan Power Company",
            raw_text="Monthly electricity bill payment"
        )
        
        category = self.category_config.categorize_receipt(receipt)
        assert category == "Utilities"
    
    def test_categorize_healthcare(self):
        """Test healthcare categorization"""
        receipt = ReceiptData(
            merchant="City Hospital",
            raw_text="Medical consultation and prescription"
        )
        
        category = self.category_config.categorize_receipt(receipt)
        assert category == "Healthcare"
    
    def test_categorize_no_match_returns_other(self):
        """Test that unknown receipts return 'Other' category"""
        receipt = ReceiptData(
            merchant="Unknown Business",
            raw_text="Some random purchase"
        )
        
        category = self.category_config.categorize_receipt(receipt)
        assert category == "Other"
    
    def test_categorize_empty_receipt(self):
        """Test categorization with empty receipt data"""
        receipt = ReceiptData()
        
        category = self.category_config.categorize_receipt(receipt)
        assert category == "Other"
    
    def test_categorize_none_values(self):
        """Test categorization with None values"""
        receipt = ReceiptData(merchant=None, raw_text=None)
        
        category = self.category_config.categorize_receipt(receipt)
        assert category == "Other"
    
    def test_get_all_categories(self):
        """Test getting all available categories"""
        categories = self.category_config.get_all_categories()
        
        assert isinstance(categories, dict)
        assert 'Food & Dining' in categories
        assert 'Transportation' in categories
        assert 'Shopping' in categories
        assert 'Other' in categories
        
        # Each category should have keywords and merchants
        for category, config in categories.items():
            assert 'keywords' in config
            assert 'merchants' in config
            assert isinstance(config['keywords'], list)
            assert isinstance(config['merchants'], list)
    
    def test_add_custom_category(self):
        """Test adding a custom category"""
        self.category_config.add_custom_category(
            "Custom Category",
            ["custom", "test"],
            ["custom_merchant"]
        )
        
        categories = self.category_config.get_all_categories()
        assert "Custom Category" in categories
        assert "custom" in categories["Custom Category"]["keywords"]
        assert "custom_merchant" in categories["Custom Category"]["merchants"]
    
    def test_custom_category_categorization(self):
        """Test categorization with custom category"""
        self.category_config.add_custom_category(
            "Pet Supplies",
            ["pet", "dog", "cat"],
            ["petstore"]
        )
        
        receipt = ReceiptData(
            merchant="PetStore Inc",
            raw_text="Dog food and pet toys"
        )
        
        category = self.category_config.categorize_receipt(receipt)
        assert category == "Pet Supplies"
    
    def test_add_keyword_to_existing_category(self):
        """Test adding keyword to existing category"""
        self.category_config.add_keyword_to_category("Food & Dining", "bakery")
        
        categories = self.category_config.get_all_categories()
        assert "bakery" in categories["Food & Dining"]["keywords"]
    
    def test_add_keyword_to_custom_category(self):
        """Test adding keyword to custom category"""
        self.category_config.add_custom_category(
            "Test Category",
            ["test"],
            []
        )
        
        self.category_config.add_keyword_to_category("Test Category", "new_keyword")
        
        categories = self.category_config.get_all_categories()
        assert "new_keyword" in categories["Test Category"]["keywords"]
    
    def test_case_insensitive_matching(self):
        """Test that keyword matching is case insensitive"""
        receipt = ReceiptData(
            merchant="STARBUCKS COFFEE",
            raw_text="COFFEE PURCHASE AT CAFE"
        )
        
        category = self.category_config.categorize_receipt(receipt)
        assert category == "Food & Dining"
    
    def test_partial_keyword_matching(self):
        """Test that partial keyword matching works"""
        receipt = ReceiptData(
            merchant="Best Restaurant Ever",
            raw_text="Great dining experience"
        )
        
        category = self.category_config.categorize_receipt(receipt)
        assert category == "Food & Dining"