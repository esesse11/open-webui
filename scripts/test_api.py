#!/usr/bin/env python3
"""Test Open WebUI API endpoints"""

import requests
import json
import time

# Wait for server to be ready
time.sleep(2)

# Test 1: Custom OpenAI API - List Models
print("=" * 50)
print("TEST 1: Custom OpenAI Models")
print("=" * 50)
try:
    response = requests.get('http://localhost:8001/api/v1/custom/models', timeout=5)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Connection error: {e}")

# Test 2: Gemini Models
print("\n" + "=" * 50)
print("TEST 2: Gemini Models")
print("=" * 50)
try:
    response = requests.get('http://localhost:8001/api/v1/gemini/models', timeout=5)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Connection error: {e}")

# Test 3: Check main API
print("\n" + "=" * 50)
print("TEST 3: Main API Health Check")
print("=" * 50)
try:
    response = requests.get('http://localhost:8001/api/v1/models', timeout=5)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Models count: {len(data) if isinstance(data, list) else 'N/A'}")
except Exception as e:
    print(f"Connection error: {e}")

print("\n" + "=" * 50)
print("✅ API 테스트 완료!")
print("=" * 50)
