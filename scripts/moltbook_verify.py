import requests
import sys

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

url = "https://www.moltbook.com/api/v1/verify"
headers = {
    "Authorization": "Bearer moltbook_sk_6GjTuKyA5jt6lyjOLXdhML_5fDC7by9K",
    "Content-Type": "application/json"
}
payload = {
    "verification_code": "moltbook_verify_22a0190e3e6dc58f3638ada7974cebe7",
    "answer": "544.00"
}

try:
    response = requests.post(url, headers=headers, json=payload)
    print(response.text)
except Exception as e:
    print(f"Error: {e}")
