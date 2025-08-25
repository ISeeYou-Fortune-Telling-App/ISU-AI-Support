"""
Test script for update data functionality
"""
import requests
import json

def test_update_data_txt():
    """Test updating data.txt file"""
    print("🔄 Testing data.txt update")
    
    # Create test content
    test_content = """
# Test Data Update
Napoleon Bonaparte test update content.
This is a test to verify the update functionality works correctly.
Updated at: 2025-08-25 13:30:00
    """.strip()
    
    # Prepare files for upload
    files = {
        'file': ('test_data.txt', test_content, 'text/plain')
    }
    data = {
        'force_reindex': True
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/update/data.txt",
            files=files,
            data=data
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ data.txt update successful!")
        else:
            print("❌ data.txt update failed!")
            
    except Exception as e:
        print(f"❌ Error testing data.txt update: {e}")

def test_update_data_json():
    """Test updating data.json file"""
    print("\n🔄 Testing data.json update")
    
    # Create test JSON content
    test_json = {
        "test_update": True,
        "timestamp": "2025-08-25 13:30:00",
        "napoleon": {
            "name": "Napoleon Bonaparte",
            "battles": ["Test Battle", "Updated Battle"],
            "status": "Updated via API"
        }
    }
    
    test_content = json.dumps(test_json, indent=2, ensure_ascii=False)
    
    # Prepare files for upload
    files = {
        'file': ('test_data.json', test_content, 'application/json')
    }
    data = {
        'force_reindex': True
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/update/data.json",
            files=files,
            data=data
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ data.json update successful!")
        else:
            print("❌ data.json update failed!")
            
    except Exception as e:
        print(f"❌ Error testing data.json update: {e}")

def test_query_after_update():
    """Test querying after update to verify new content"""
    print("\n🔍 Testing query after update")
    
    query_data = {
        "query": "test update",
        "mode": "mix"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/query",
            json=query_data
        )
        
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Answer: {result.get('answer', 'No answer')[:100]}...")
        
        if "test" in result.get('answer', '').lower():
            print("✅ Update content found in query results!")
        else:
            print("⚠️ Update content not found in query results")
            
    except Exception as e:
        print(f"❌ Error testing query: {e}")

if __name__ == "__main__":
    print("🧪 Testing Update Data Functionality")
    print("=" * 50)
    
    test_update_data_txt()
    test_update_data_json()
    test_query_after_update()
    
    print("\n🏁 Update tests completed!")
