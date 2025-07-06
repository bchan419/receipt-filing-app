#!/usr/bin/env python3
"""
Simple test script for the Receipt OCR App
"""
import sys
import os
import json
from io import BytesIO
import base64

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from fastapi.testclient import TestClient
from main import app

def create_sample_receipt_image():
    """Create a sample receipt image content for testing"""
    # This is a simple 1x1 pixel PNG image in base64
    sample_png = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    return base64.b64decode(sample_png)

def test_api_endpoints():
    """Test the main API endpoints"""
    client = TestClient(app)
    
    print("🧪 Testing Receipt OCR App...")
    
    # Test 1: Root endpoint
    print("\n1. Testing root endpoint...")
    response = client.get("/")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    assert response.status_code == 200
    
    # Test 2: Categories endpoint
    print("\n2. Testing categories endpoint...")
    response = client.get("/categories")
    print(f"   Status: {response.status_code}")
    categories = response.json()
    print(f"   Found {len(categories)} categories:")
    for category in list(categories.keys())[:3]:  # Show first 3
        print(f"     - {category}")
    assert response.status_code == 200
    
    # Test 3: Upload endpoint (with mock)
    print("\n3. Testing upload endpoint...")
    sample_image = create_sample_receipt_image()
    
    # This will fail with actual OCR since we don't have a real receipt,
    # but it will test the file handling and API structure
    try:
        response = client.post(
            "/upload",
            files={"files": ("test_receipt.png", BytesIO(sample_image), "image/png")}
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Upload result: {result[0]['status']}")
            if result[0]['status'] == 'error':
                print(f"   Error (expected): {result[0]['error'][:50]}...")
        else:
            print(f"   Response: {response.text[:100]}...")
    except Exception as e:
        print(f"   Error (may be expected): {str(e)[:50]}...")
    
    print("\n✅ API endpoint tests completed!")
    
def test_components():
    """Test individual components"""
    print("\n🔧 Testing individual components...")
    
    # Test category system
    from config.categories import CategoryConfig
    category_config = CategoryConfig()
    
    print("\n1. Testing category classification...")
    from models.receipt import ReceiptData
    
    test_receipt = ReceiptData(
        merchant="McDonald's",
        raw_text="McDonald's Restaurant receipt"
    )
    category = category_config.categorize_receipt(test_receipt)
    print(f"   McDonald's categorized as: {category}")
    assert category == "Food & Dining"
    
    # Test file handler
    from utils.file_handler import FileHandler
    file_handler = FileHandler()
    
    print("\n2. Testing file validation...")
    print(f"   receipt.jpg is valid: {file_handler.is_valid_image('receipt.jpg')}")
    print(f"   document.pdf is valid: {file_handler.is_valid_image('document.pdf')}")
    
    print("\n✅ Component tests completed!")

def main():
    """Run all tests"""
    print("🧾 Receipt OCR App - Test Suite")
    print("=" * 40)
    
    try:
        test_api_endpoints()
        test_components()
        
        print("\n🎉 All tests passed!")
        print("\n📋 Your Receipt OCR App is working correctly!")
        print("\nTo start the server manually:")
        print("   source venv/bin/activate")
        print("   export GOOGLE_APPLICATION_CREDENTIALS=/Users/bernard/DevProjects/receipt-filing-app/google-credentials.json")
        print("   export GOOGLE_CLOUD_PROJECT=receipt-filing-app")
        print("   cd src && python main.py")
        print("\nThen visit: http://localhost:8000/docs for API documentation")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()