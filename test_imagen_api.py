"""
Test Imagen API directly to see detailed error
"""
import requests
import os
import json

# Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "your-api-key-here")
API_BASE_URL = "https://us-central1-aiplatform.googleapis.com/v1"
MODEL = "imagen-3.0-generate-002"

def test_imagen_predict():
    """Test Imagen API with :predict endpoint"""
    print("=" * 60)
    print("Testing Imagen API - :predict endpoint")
    print("=" * 60)

    url = f"{API_BASE_URL}/models/{MODEL}:predict"

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GOOGLE_API_KEY,
    }

    data = {
        "instances": {
            "prompt": "귀여운 고양이"
        },
        "parameters": {
            "sampleCount": 1,
            "outputOptions": {
                "mimeType": "image/png"
            }
        }
    }

    print(f"\nURL: {url}")
    print(f"Headers: {json.dumps(headers, indent=2)}")
    print(f"Data: {json.dumps(data, indent=2)}")
    print("\nSending request...")

    try:
        response = requests.post(url, headers=headers, json=data, timeout=60)

        print(f"\nStatus Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")

        if response.status_code == 200:
            print("\n✅ SUCCESS!")
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)[:500]}...")
        else:
            print("\n❌ FAILED!")
            print(f"Error Response: {response.text}")

    except Exception as e:
        print(f"\n❌ EXCEPTION!")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

def test_imagen_generateContent():
    """Test Imagen API with :generateContent endpoint"""
    print("\n" + "=" * 60)
    print("Testing Imagen API - :generateContent endpoint")
    print("=" * 60)

    url = f"{API_BASE_URL}/models/{MODEL}:generateContent"

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GOOGLE_API_KEY,
    }

    data = {
        "contents": [{
            "parts": [{
                "text": "귀여운 고양이"
            }]
        }]
    }

    print(f"\nURL: {url}")
    print(f"Headers: {json.dumps(headers, indent=2)}")
    print(f"Data: {json.dumps(data, indent=2)}")
    print("\nSending request...")

    try:
        response = requests.post(url, headers=headers, json=data, timeout=60)

        print(f"\nStatus Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")

        if response.status_code == 200:
            print("\n✅ SUCCESS!")
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)[:500]}...")
        else:
            print("\n❌ FAILED!")
            print(f"Error Response: {response.text}")

    except Exception as e:
        print(f"\n❌ EXCEPTION!")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

def test_wrong_model():
    """Test with wrong model (gemini-2.5-pro) to see error"""
    print("\n" + "=" * 60)
    print("Testing with WRONG model - gemini-2.5-pro")
    print("=" * 60)

    wrong_model = "gemini-2.5-pro"
    url = f"{API_BASE_URL}/models/{wrong_model}:predict"

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GOOGLE_API_KEY,
    }

    data = {
        "instances": {
            "prompt": "귀여운 고양이"
        },
        "parameters": {
            "sampleCount": 1,
            "outputOptions": {
                "mimeType": "image/png"
            }
        }
    }

    print(f"\nURL: {url}")
    print("\nSending request...")

    try:
        response = requests.post(url, headers=headers, json=data, timeout=60)

        print(f"\nStatus Code: {response.status_code}")

        if response.status_code == 200:
            print("\n✅ Unexpected success!")
        else:
            print("\n❌ EXPECTED FAILURE!")
            print(f"Error Response: {response.text}")

    except Exception as e:
        print(f"\n❌ EXCEPTION!")
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    print("Google Imagen API Test Script")
    print("=" * 60)

    if GOOGLE_API_KEY == "your-api-key-here":
        print("\n⚠️  WARNING: Please set GOOGLE_API_KEY environment variable")
        print("   or edit this script to add your API key")
        print("\nUsage:")
        print("  set GOOGLE_API_KEY=your-actual-key")
        print("  python test_imagen_api.py")
    else:
        print(f"\nAPI Key: {GOOGLE_API_KEY[:10]}...{GOOGLE_API_KEY[-5:]}")
        print(f"API Base URL: {API_BASE_URL}")
        print(f"Model: {MODEL}")

    print("\n")
    input("Press Enter to start tests...")

    # Run tests
    test_imagen_predict()

    print("\n" + "=" * 60)
    input("Press Enter to test :generateContent endpoint...")
    test_imagen_generateContent()

    print("\n" + "=" * 60)
    input("Press Enter to test WRONG model (to see error)...")
    test_wrong_model()

    print("\n" + "=" * 60)
    print("Tests completed!")
    print("=" * 60)
