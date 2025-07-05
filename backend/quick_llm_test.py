#!/usr/bin/env python3
"""
Quick LLM Connection Test
"""

import requests
import json

def quick_test():
    print("Testing Ollama connection...")
    
    try:
        # Test 1: Check if Ollama is running
        response = requests.get("http://127.0.0.1:11434/api/tags", timeout=5)
        print(f"Ollama server status: {response.status_code}")
        
        if response.status_code == 200:
            models = response.json()
            print(f"Available models: {[m['name'] for m in models.get('models', [])]}")
            
            # Test 2: Simple LLM request
            if models.get('models'):
                model_name = models['models'][0]['name']
                print(f"Testing with model: {model_name}")
                
                llm_response = requests.post(
                    "http://127.0.0.1:11434/api/generate",
                    json={
                        "model": model_name,
                        "prompt": "Say 'Hello World' and nothing else.",
                        "stream": False
                    },
                    timeout=30
                )
                
                if llm_response.status_code == 200:
                    result = llm_response.json()
                    print(f"LLM Response: {result.get('response', 'No response')}")
                    print("✅ LLM is working!")
                else:
                    print(f"❌ LLM request failed: {llm_response.status_code}")
            else:
                print("❌ No models available")
        else:
            print("❌ Ollama server not responding")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    quick_test()
