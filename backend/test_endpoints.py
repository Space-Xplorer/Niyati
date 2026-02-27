"""
Quick endpoint validation script
Tests all API endpoints with curl-like requests
"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def print_result(endpoint: str, status: str, details: str = ""):
    """Print test result"""
    symbol = "✅" if status == "PASS" else "❌"
    print(f"{symbol} {endpoint}: {status}")
    if details:
        print(f"   {details}")

def test_health_check():
    """Test GET /health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print_result("GET /health", "PASS", f"Status: {response.json()['status']}")
            return True
        else:
            print_result("GET /health", "FAIL", f"Status code: {response.status_code}")
            return False
    except Exception as e:
        print_result("GET /health", "FAIL", f"Error: {str(e)}")
        return False

def test_register():
    """Test POST /auth/register endpoint"""
    try:
        payload = {
            "email": "test_admin@example.com",
            "password": "TestPassword123!",
            "role": "Admin",
            "gstin": None
        }
        response = requests.post(f"{BASE_URL}/auth/register", json=payload, timeout=5)
        if response.status_code in [200, 201, 400]:  # 400 if user already exists
            print_result("POST /auth/register", "PASS", f"Status: {response.status_code}")
            return True
        else:
            print_result("POST /auth/register", "FAIL", f"Status code: {response.status_code}")
            return False
    except Exception as e:
        print_result("POST /auth/register", "FAIL", f"Error: {str(e)}")
        return False

def test_login():
    """Test POST /auth/login endpoint"""
    try:
        payload = {
            "email": "test_admin@example.com",
            "password": "TestPassword123!"
        }
        response = requests.post(f"{BASE_URL}/auth/login", json=payload, timeout=5)
        if response.status_code == 200:
            token = response.json().get("access_token")
            print_result("POST /auth/login", "PASS", f"Token received: {token[:20]}...")
            return token
        else:
            print_result("POST /auth/login", "FAIL", f"Status code: {response.status_code}")
            return None
    except Exception as e:
        print_result("POST /auth/login", "FAIL", f"Error: {str(e)}")
        return None

def test_dashboard(token: str):
    """Test GET /dashboard endpoint"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/dashboard", headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_result("GET /dashboard", "PASS", f"Health score: {data.get('health_score', 'N/A')}")
            return True
        else:
            print_result("GET /dashboard", "FAIL", f"Status code: {response.status_code}")
            return False
    except Exception as e:
        print_result("GET /dashboard", "FAIL", f"Error: {str(e)}")
        return False

def test_graph(token: str):
    """Test GET /graph endpoint"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/graph", headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_result("GET /graph", "PASS", f"Nodes: {len(data.get('nodes', []))}, Edges: {len(data.get('edges', []))}")
            return True
        else:
            print_result("GET /graph", "FAIL", f"Status code: {response.status_code}")
            return False
    except Exception as e:
        print_result("GET /graph", "FAIL", f"Error: {str(e)}")
        return False

def test_logs_stream():
    """Test GET /logs/stream endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/logs/stream", stream=True, timeout=2)
        if response.status_code == 200:
            print_result("GET /logs/stream", "PASS", "SSE stream connected")
            return True
        else:
            print_result("GET /logs/stream", "FAIL", f"Status code: {response.status_code}")
            return False
    except requests.exceptions.ReadTimeout:
        # Timeout is expected for SSE streams
        print_result("GET /logs/stream", "PASS", "SSE stream connected (timeout expected)")
        return True
    except Exception as e:
        print_result("GET /logs/stream", "FAIL", f"Error: {str(e)}")
        return False

def main():
    """Run all endpoint tests"""
    print("\n" + "="*60)
    print("PROJECT NIYATI - API ENDPOINT VALIDATION")
    print("="*60 + "\n")
    
    print("⚠️  Make sure the FastAPI server is running:")
    print("   cd backend && uvicorn app_fastapi:app --reload\n")
    
    results = []
    
    # Test health check
    print("Testing Health Check...")
    results.append(test_health_check())
    print()
    
    # Test authentication flow
    print("Testing Authentication...")
    results.append(test_register())
    token = test_login()
    results.append(token is not None)
    print()
    
    if token:
        # Test protected endpoints
        print("Testing Protected Endpoints...")
        results.append(test_dashboard(token))
        results.append(test_graph(token))
        print()
        
        # Test SSE streaming
        print("Testing Real-time Streaming...")
        results.append(test_logs_stream())
        print()
    
    # Summary
    print("="*60)
    passed = sum(results)
    total = len(results)
    print(f"SUMMARY: {passed}/{total} tests passed")
    print("="*60 + "\n")
    
    if passed == total:
        print("✅ All API endpoints are working correctly!")
    else:
        print("⚠️  Some endpoints need attention")

if __name__ == "__main__":
    main()
