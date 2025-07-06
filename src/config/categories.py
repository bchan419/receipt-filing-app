from typing import Dict, List, Optional
from models.receipt import ReceiptData

class CategoryConfig:
    """Configurable expense categories for receipt classification"""
    
    def __init__(self):
        self.default_categories = {
            'Food & Dining': {
                'keywords': ['restaurant', '餐廳', 'cafe', '咖啡', 'food', '食物', 'dining', 'meal', '飯店', 'bar', '酒吧'],
                'merchants': ['mcdonalds', 'starbucks', 'subway', '麥當勞', '星巴克']
            },
            'Transportation': {
                'keywords': ['uber', 'taxi', '計程車', 'mrt', '捷運', 'bus', '公車', 'train', '火車', 'parking', '停車'],
                'merchants': ['uber', 'grab', 'taxi', 'mrt']
            },
            'Shopping': {
                'keywords': ['mart', '超市', 'store', '商店', 'shop', '購物', 'market', '市場', 'mall', '商場'],
                'merchants': ['7-eleven', 'familymart', 'walmart', 'target', '全家', '7-11']
            },
            'Utilities': {
                'keywords': ['electric', '電力', 'water', '水費', 'gas', '瓦斯', 'internet', '網路', 'phone', '電話'],
                'merchants': ['台電', '自來水', '中華電信']
            },
            'Healthcare': {
                'keywords': ['hospital', '醫院', 'clinic', '診所', 'pharmacy', '藥局', 'doctor', '醫生', 'medical', '醫療'],
                'merchants': ['hospital', 'clinic']
            },
            'Entertainment': {
                'keywords': ['movie', '電影', 'cinema', '戲院', 'game', '遊戲', 'book', '書', 'music', '音樂'],
                'merchants': ['netflix', 'spotify', 'cinema']
            },
            'Office Supplies': {
                'keywords': ['stationery', '文具', 'office', '辦公', 'paper', '紙張', 'pen', '筆', 'computer', '電腦'],
                'merchants': ['office depot', 'staples']
            },
            'Other': {
                'keywords': [],
                'merchants': []
            }
        }
        
        # User can add custom categories
        self.custom_categories = {}
    
    def categorize_receipt(self, receipt_data: ReceiptData) -> str:
        """Categorize receipt based on merchant and text content"""
        if not receipt_data.merchant and not receipt_data.raw_text:
            return 'Other'
        
        merchant = (receipt_data.merchant or '').lower()
        text = (receipt_data.raw_text or '').lower()
        
        # Check all categories (custom first, then default)
        all_categories = {**self.custom_categories, **self.default_categories}
        
        for category, config in all_categories.items():
            # Check merchant matches first (more specific)
            for merchant_pattern in config['merchants']:
                if merchant_pattern.lower() in merchant:
                    return category
            
            # Check keyword matches (be more restrictive to avoid false positives)
            for keyword in config['keywords']:
                keyword_lower = keyword.lower()
                # Require word boundaries or start of string for better matching
                import re
                pattern = r'\b' + re.escape(keyword_lower) + r'\b'
                if re.search(pattern, text) or re.search(pattern, merchant):
                    return category
        
        return 'Other'
    
    def get_all_categories(self) -> Dict[str, Dict]:
        """Get all available categories"""
        return {**self.default_categories, **self.custom_categories}
    
    def add_custom_category(self, name: str, keywords: List[str], merchants: List[str]):
        """Add a custom category"""
        self.custom_categories[name] = {
            'keywords': keywords,
            'merchants': merchants
        }
    
    def add_keyword_to_category(self, category: str, keyword: str):
        """Add keyword to existing category"""
        if category in self.default_categories:
            self.default_categories[category]['keywords'].append(keyword)
        elif category in self.custom_categories:
            self.custom_categories[category]['keywords'].append(keyword)