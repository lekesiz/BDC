#!/usr/bin/env python
"""Test beneficiary creation with real user."""

import requests

# Real user token from the browser
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc0NzM1ODYwMSwianRpIjoiMGMwMmI5OTktNTJiMS00Y2JlLTkwNWItOTNlZDMyZjAwNDM3IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6MSwibmJmIjoxNzQ3MzU4NjAxLCJjc3JmIjoiYzRmOTc0NzktYWIyYi00ZGJhLTg5OGEtNzczYTg2YmFhMjkxIiwiZXhwIjoxNzQ3MzYyMjAxfQ.8aCASGHV3I67EAirbcc-2T6lXtTAWJlic6Gye8TkTl8"

# Same data from frontend
data = {
    "first_name": "Mikail",
    "last_name": "Lekesiz",
    "email": "mikail@lekesiz.fr",
    "phone": "",
    "birth_date": "",
    "address": "",
    "bio": "",
    "category": "",
    "city": "",
    "country": "",
    "custom_fields": {},
    "education_level": "",
    "gender": "",
    "goals": "",
    "nationality": "",
    "native_language": "",
    "notes": "",
    "occupation": "",
    "organization": "",
    "referral_source": "",
    "state": "",
    "status": "active",
    "zip_code": ""
}

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

response = requests.post("http://localhost:5001/api/beneficiaries", 
                       json=data, 
                       headers=headers)

print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
print(f"Headers: {response.headers}")