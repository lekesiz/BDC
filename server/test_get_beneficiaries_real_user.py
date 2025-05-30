#!/usr/bin/env python
"""Test GET beneficiaries with real user token."""

import requests

# Real user token from the browser
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc0NzM1ODYwMSwianRpIjoiMGMwMmI5OTktNTJiMS00Y2JlLTkwNWItOTNlZDMyZjAwNDM3IiwidHlwZSI6ImFjY2VzcyIsInN1YiI6MSwibmJmIjoxNzQ3MzU4NjAxLCJjc3JmIjoiYzRmOTc0NzktYWIyYi00ZGJhLTg5OGEtNzczYTg2YmFhMjkxIiwiZXhwIjoxNzQ3MzYyMjAxfQ.8aCASGHV3I67EAirbcc-2T6lXtTAWJlic6Gye8TkTl8"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

params = {
    "page": 1,
    "per_page": 10,
    "sort_by": "created_at",
    "sort_dir": "desc"
}

response = requests.get("http://localhost:5001/api/beneficiaries", 
                      params=params,
                      headers=headers)

print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
print(f"Headers: {response.headers}")