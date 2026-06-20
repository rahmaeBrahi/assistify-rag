"""
RAG System Test Suite
Run after deployment: python manage.py shell < test_rag.py
Or: python test_rag.py (from backend/ directory with Django configured)
"""
import os
import sys
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "assistify.settings.base")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    django.setup()
except Exception as e:
    print(f"Django setup skipped (no DB): {e}")

import json
import urllib.request

BASE_URL = os.environ.get("TEST_BASE_URL", "http://localhost:8000")
PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"

def test(name, ok, detail=""):
    status = PASS if ok else FAIL
    print(f"  [{status}] {name}" + (f" — {detail}" if detail else ""))
    return ok


def request(path, method="GET", body=None):
    url = f"{BASE_URL}{path}"
    data = json.dumps(body).encode() if body else None
    headers = {"Content-Type": "application/json"} if data else {}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, {}
    except Exception as e:
        return 0, {"error": str(e)}


print("\n======= Assistify RAG Test Suite =======\n")
all_pass = True

# --- 1. Health Check ---
print("1. Health Check")
code, data = request("/api/health/")
ok = code == 200 and data.get("status") == "healthy"
all_pass &= test("GET /api/health/ returns 200", ok, f"status={data.get('status')}")
all_pass &= test("LLM configured", data.get("services", {}).get("llm_configured", False))

# --- 2. Chat endpoint — English ---
print("\n2. Chat Endpoint (English)")
code, data = request("/api/v1/chat/", "POST", {"message": "Hello, what products do you have?"})
ok = code == 200 and bool(data.get("reply") or data.get("response"))
all_pass &= test("POST /api/v1/chat/ returns 200", code == 200, f"code={code}")
all_pass &= test("Response contains text", ok, f"reply={str(data.get('reply',''))[:60]}")
all_pass &= test("conversation_id returned", bool(data.get("conversation_id")))

conv_id = data.get("conversation_id")

# --- 3. Chat endpoint — Arabic ---
print("\n3. Chat Endpoint (Arabic)")
code, data = request("/api/v1/chat/", "POST", {
    "message": "مرحبا، عندك جهاز قياس الضغط؟",
    "conversation_id": conv_id
})
all_pass &= test("Arabic message accepted", code == 200, f"code={code}")
all_pass &= test("Arabic/multilingual response", bool(data.get("reply") or data.get("response")))

# --- 4. Follow-up (conversation memory) ---
print("\n4. Conversation Memory")
code, data = request("/api/v1/chat/", "POST", {
    "message": "What is its price?",
    "conversation_id": conv_id
})
all_pass &= test("Follow-up message works", code == 200, f"code={code}")

# --- 5. Empty message validation ---
print("\n5. Input Validation")
code, data = request("/api/v1/chat/", "POST", {"message": ""})
all_pass &= test("Empty message rejected (400)", code == 400, f"code={code}")

# --- 6. Products API still works ---
print("\n6. Products API")
code, data = request("/api/v1/products/")
all_pass &= test("GET /api/v1/products/ returns 200", code == 200, f"code={code}")

print(f"\n{'='*40}")
if all_pass:
    print(f"  \033[92mAll tests passed!\033[0m")
else:
    print(f"  \033[91mSome tests failed — check logs above.\033[0m")
print(f"{'='*40}\n")
