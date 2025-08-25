#!/usr/bin/env python3
"""
Test script để kiểm tra dữ liệu từ file JSON
"""

import requests
import json

def test_json_data_queries():
    """Test các câu hỏi liên quan đến dữ liệu JSON"""
    
    base_url = "http://localhost:8000"
    
    test_cases = [
        {
            "question": "Trận Austerlitz là gì?",
            "description": "Hỏi về trận chiến từ JSON data",
            "expect_json": True
        },
        {
            "question": "Napoleon có những tướng thần cận nào?",
            "description": "Hỏi về thần cận từ JSON data", 
            "expect_json": True
        },
        {
            "question": "Trận Waterloo diễn ra khi nào?",
            "description": "Hỏi về trận chiến từ JSON data",
            "expect_json": True
        },
        {
            "question": "Marshal nào được gọi là tướng dũng cảm nhất?",
            "description": "Hỏi về Marshal từ JSON data",
            "expect_json": True
        },
        {
            "question": "Garde Impériale là gì?",
            "description": "Hỏi về Vệ binh Hoàng gia từ JSON data",
            "expect_json": True
        },
        {
            "question": "Chiến dịch Nga diễn ra năm nào?",
            "description": "Hỏi về sự kiện trong timeline JSON",
            "expect_json": True
        }
    ]
    
    print("📊 Testing JSON Data Integration")
    print("=" * 50)
    
    success_count = 0
    total_count = len(test_cases)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔍 Test {i}: {test_case['description']}")
        print(f"Question: '{test_case['question']}'")
        
        try:
            response = requests.post(
                f"{base_url}/query",
                json={
                    "question": test_case["question"],
                    "mode": "mix",
                    "top_k": 5
                },
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get("answer", "No answer")
                
                # Truncate long answers
                display_answer = answer[:200] + "..." if len(answer) > 200 else answer
                
                print(f"✅ Status: {response.status_code}")
                print(f"Answer: {display_answer}")
                print(f"Mode: {data.get('mode', 'unknown')}")
                
                # Check answer quality
                if "[no-context]" in answer:
                    print("⚠️  Warning: No context found")
                elif len(answer.strip()) < 20:
                    print("⚠️  Warning: Very short answer") 
                else:
                    print("✅ Good answer received")
                    success_count += 1
                    
                # Check if answer contains JSON-specific information
                json_indicators = [
                    "1805", "Austerlitz", "Michel Ney", "Garde Impériale", 
                    "Marshal", "1812", "Borodino", "Leipzig", "tướng thần cận",
                    "Vệ binh Hoàng gia", "Jean Lannes", "dũng cảm nhất"
                ]
                
                has_json_info = any(indicator in answer for indicator in json_indicators)
                if has_json_info and test_case["expect_json"]:
                    print("🎯 Contains JSON-specific information")
                elif test_case["expect_json"]:
                    print("⚠️  May not contain JSON-specific information")
                    
            else:
                print(f"❌ Error: Status {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
        
        print("-" * 40)
    
    print(f"\n🏁 JSON Data Test Results: {success_count}/{total_count} tests successful")
    
    if success_count == total_count:
        print("🎉 All JSON data tests passed!")
    elif success_count > total_count * 0.7:
        print("✅ Most JSON data tests passed!")
    else:
        print("⚠️  Some JSON data tests failed - check data integration")

if __name__ == "__main__":
    test_json_data_queries()
