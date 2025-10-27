#!/usr/bin/env python3
"""
Test script for o3-deep-research API endpoint
"""

import asyncio
import aiohttp
import json
import sys
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8001/openai"
MODEL = "o3-deep-research"
QUERY = "각종 sns 최신 언급량이 높은 패션 관련 트렌드 조사"

# Read API key from environment
import os
API_KEY = os.getenv("OPENAI_API_KEY")

if not API_KEY:
    print("❌ Error: OPENAI_API_KEY environment variable not set")
    print("Please set it in .env or export it")
    sys.exit(1)


async def test_o3_deep_research():
    """Test o3-deep-research API endpoint"""

    print("=" * 80)
    print(f"🧪 Testing o3-deep-research API")
    print("=" * 80)
    print(f"⏰ Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔗 API URL: {API_BASE_URL}/v1/chat/completions")
    print(f"📝 Model: {MODEL}")
    print(f"❓ Query: {QUERY[:100]}...")
    print("-" * 80)

    # Prepare request payload
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "user", "content": QUERY}
        ],
        "max_completion_tokens": 16000,
        "temperature": 1.0,
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
    }

    try:
        async with aiohttp.ClientSession() as session:
            print("\n📤 Sending request...")

            async with session.post(
                f"{API_BASE_URL}/v1/chat/completions",
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=300),  # 5 minute timeout
            ) as response:
                print(f"📥 Response status: {response.status}")

                response_text = await response.text()

                if response.status == 200:
                    response_data = json.loads(response_text)

                    print("\n" + "=" * 80)
                    print("✅ SUCCESS!")
                    print("=" * 80)

                    # Extract content
                    if "choices" in response_data and response_data["choices"]:
                        content = response_data["choices"][0]["message"]["content"]
                        print(f"\n📄 Response Content:\n")
                        print("-" * 80)
                        print(content[:2000])  # Print first 2000 chars
                        if len(content) > 2000:
                            print(f"\n... (content truncated, total length: {len(content)} chars)")
                        print("-" * 80)

                    # Print usage stats
                    if "usage" in response_data:
                        usage = response_data["usage"]
                        print(f"\n📊 Usage Statistics:")
                        print(f"  - Input tokens: {usage.get('prompt_tokens', 'N/A')}")
                        print(f"  - Output tokens: {usage.get('completion_tokens', 'N/A')}")
                        print(f"  - Total tokens: {usage.get('total_tokens', 'N/A')}")

                    print(f"\n⏰ End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

                else:
                    print("\n" + "=" * 80)
                    print(f"❌ ERROR: Status {response.status}")
                    print("=" * 80)

                    try:
                        error_data = json.loads(response_text)
                        print(f"\n📋 Error Response:")
                        print(json.dumps(error_data, indent=2, ensure_ascii=False))
                    except:
                        print(f"\n📋 Error Response:")
                        print(response_text[:1000])

    except asyncio.TimeoutError:
        print("\n❌ ERROR: Request timeout (> 5 minutes)")
        print("This might mean o3-deep-research is still processing")
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n🚀 o3-deep-research API Test\n")

    try:
        asyncio.run(test_o3_deep_research())
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
        sys.exit(0)
