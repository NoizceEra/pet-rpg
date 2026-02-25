import requests
import sys

# Ensure UTF-8 output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

api_key = "moltbook_sk_6GjTuKyA5jt6lyjOLXdhML_5fDC7by9K"
url = "https://www.moltbook.com/api/v1/verify"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

payload = {
    "verification_code": "moltbook_verify_f829cde4a30129adf2b841d9c7899b84",
    "answer": "67.00"
}

try:
    response = requests.post(url, headers=headers, json=payload)
    print(response.text)
except Exception as e:
    print(f"Error: {e}")
