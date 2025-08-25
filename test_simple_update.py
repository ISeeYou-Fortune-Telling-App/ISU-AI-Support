#!/usr/bin/env python3
"""
Simple test for update endpoints
"""

import requests
import io

def test_simple_update():
    """Test simple file update"""
    
    print("🔄 Testing simple data.txt update")
    
    # Tạo content test đơn giản
    test_content = "This is updated test content for data.txt file."
    
    # Tạo file-like object
    test_file = io.BytesIO(test_content.encode('utf-8'))
    
    # Gửi request
    try:
        response = requests.post(
            "http://localhost:8000/update/data.txt",
            files={'file': ('data.txt', test_file, 'text/plain')},
            data={'force_reindex': 'true'}
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('status') == 'success':
                print("✅ Update successful!")
            else:
                print(f"❌ Update failed: {result.get('message')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_simple_update()
