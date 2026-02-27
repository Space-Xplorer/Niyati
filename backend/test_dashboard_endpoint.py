"""
Test dashboard endpoint
"""
import requests
import jwt
from datetime import datetime, timedelta
from auth import get_secret_key

# Create a test token for business user
token = jwt.encode({
    'user_id': 4,
    'role': 'Business_Owner',
    'gstin': '29AABCT1332L1Z5',
    'exp': datetime.utcnow() + timedelta(hours=24)
}, get_secret_key(), algorithm="HS256")

print(f"Test token: {token[:50]}...")

# Test dashboard endpoint
url = 'http://127.0.0.1:5000/dashboard'
headers = {'Authorization': f'Bearer {token}'}

print(f"\nTesting GET {url}")
print(f"Headers: {headers}")

try:
    response = requests.get(url, headers=headers)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {response.text[:500]}")
except Exception as e:
    print(f"\nError: {str(e)}")
