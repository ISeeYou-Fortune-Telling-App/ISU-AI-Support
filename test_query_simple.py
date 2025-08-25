#!/usr/bin/env python3
"""
Test query with updated content
"""

import requests

def test_query():
    """Test query endpoint after update"""
    
    print("🔍 Testing query endpoint")
    
    # Test query đơn giản
    query_data = {
        "question": "What is the content?",
        "mode": "local"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/query",
            json=query_data
        )
        
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Answer: {result.get('answer', 'No answer')}")
            print("✅ Query successful!")
        else:
            print(f"Response: {response.text}")
            print(f"❌ Query failed with status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_query()
