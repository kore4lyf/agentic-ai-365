import httpx
import json

JAN_URL = "http://127.0.0.1:1337/v1/chat/completions"
MODEL_NAME = "LFM2_5-350M-Q4_K_M"

print("🧪 Testing JAN API with httpx...\n")

# Build the exact payload your agent sends
payload = {
    "model": MODEL_NAME,
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hi"}
    ],
    "stream": False,
}

print(f"[TEST] URL: {JAN_URL}")
print(f"[TEST] Model: {MODEL_NAME}")
print(f"[TEST] Payload: {json.dumps(payload, indent=2)}\n")

try:
    print("[TEST] Sending request with httpx...")
    
    with httpx.Client(timeout=300) as client:
        response = client.post(JAN_URL, json=payload)
    
    print(f"[TEST] Status code: {response.status_code}")
    print(f"[TEST] Response headers: {dict(response.headers)}\n")
    
    if response.status_code == 200:
        data = response.json()
        print("[TEST] ✅ SUCCESS! Response received:")
        print(json.dumps(data, indent=2))
        
        # Extract the answer
        try:
            answer = data["choices"][0]["message"]["content"]
            print(f"\n[TEST] Agent says: {answer}")
        except KeyError as e:
            print(f"\n[TEST] ⚠️ Could not extract answer: {e}")
    else:
        print(f"[TEST] ❌ Unexpected status code: {response.status_code}")
        print(f"[TEST] Response text: {response.text}")

except httpx.TimeoutException:
    print("[TEST] ❌ REQUEST TIMED OUT (300 seconds)")
    print("[TEST] JAN might be slow or not responding")
    
except httpx.ConnectError as e:
    print(f"[TEST] ❌ CONNECTION ERROR: {e}")
    print("[TEST] Make sure JAN is running on http://127.0.0.1:1337")
    
except Exception as e:
    print(f"[TEST] ❌ UNEXPECTED ERROR: {type(e).__name__}: {e}")