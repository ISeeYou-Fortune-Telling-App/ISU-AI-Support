#!/usr/bin/env python3
"""
Test script riêng cho tiếng Việt
"""

import requests
import json

def test_vietnamese_queries():
    """Test các câu hỏi tiếng Việt"""
    
    base_url = "http://localhost:8000"
    
    test_cases = [
        {
            "question": "xin chào",
            "description": "Greeting in Vietnamese"
        },
        {
            "question": "Napoleon là ai?",
            "description": "Who is Napoleon (Vietnamese)"
        },
        {
            "question": "Napoleon sinh năm nào?",
            "description": "When was Napoleon born (Vietnamese)"
        },
        {
            "question": "hello",
            "description": "Greeting in English"
        }
    ]
    
    print("🇻🇳 Testing Vietnamese Language Support")
    print("=" * 50)
    
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
                if len(answer) > 150:
                    answer = answer[:150] + "..."
                
                print(f"✅ Status: {response.status_code}")
                print(f"Answer: {answer}")
                print(f"Mode: {data.get('mode', 'unknown')}")
                
                # Check if answer contains meaningful content
                if "[no-context]" in answer:
                    print("⚠️  Warning: No context found")
                elif len(answer.strip()) < 10:
                    print("⚠️  Warning: Very short answer")
                else:
                    print("✅ Good answer received")
                    
            else:
                print(f"❌ Error: Status {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
        
        print("-" * 30)
    
    print("\n🏁 Vietnamese test completed!")

if __name__ == "__main__":
    test_vietnamese_queries()
