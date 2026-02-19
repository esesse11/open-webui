#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import requests
import json
from datetime import datetime

# Configuration
API_URL = "http://localhost:8001/openai/v1/chat/completions"
API_KEY = os.environ.get("OPENAI_API_KEY", "")

print("=" * 80)
print("[Test] o3-deep-research API")
print("=" * 80)
print(f"Start: {datetime.now().strftime('%H:%M:%S')}")
print(f"URL: {API_URL}")
print("-" * 80)

# Prepare request
headers = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0",
}

payload = {
    "model": "o3-deep-research",
    "messages": [
        {
            "role": "user",
            "content": "What are the latest fashion trends on social media?"
        }
    ],
    "max_completion_tokens": 16000,
}

print("[Request] Sending to o3-deep-research...\n")

try:
    response = requests.post(
        API_URL,
        json=payload,
        headers=headers,
        timeout=300  # 5 minute timeout
    )

    print(f"[Response] Status: {response.status_code}")
    print("-" * 80)

    if response.status_code == 200:
        data = response.json()

        print("\n[SUCCESS]\n")

        # Extract content
        if "choices" in data and data["choices"]:
            content = data["choices"][0]["message"]["content"]
            print("[Content]:")
            print("-" * 80)
            print(content[:1500])  # First 1500 chars
            if len(content) > 1500:
                print(f"\n... (truncated, total length: {len(content)} chars)")
            print("-" * 80)

        # Print usage
        if "usage" in data:
            usage = data["usage"]
            print(f"\n[Usage]:")
            print(f"  Input tokens: {usage.get('prompt_tokens', 'N/A')}")
            print(f"  Output tokens: {usage.get('completion_tokens', 'N/A')}")
            print(f"  Total: {usage.get('total_tokens', 'N/A')}")

        print(f"\nEnd: {datetime.now().strftime('%H:%M:%S')}")

    else:
        print(f"\n[ERROR] Status {response.status_code}\n")
        print("Response:")
        try:
            print(json.dumps(response.json(), indent=2))
        except:
            print(response.text)

except Exception as e:
    print(f"\n[ERROR] {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
