#!/usr/bin/env python3
"""
Push statewide_results.json to GitHub via API — no git installation needed.
Usage: python3 push_to_github.py
Set GITHUB_TOKEN environment variable or it will prompt.
"""
import requests
import base64
import os
import sys
from datetime import datetime

REPO = 'mekcoleman/il-election-results'
FILE = 'statewide_results.json'
API_URL = f'https://api.github.com/repos/{REPO}/contents/{FILE}'

def push():
    token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
    if not token:
        token = input('GitHub Personal Access Token: ').strip()
    
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    # Read the file
    try:
        with open(FILE, 'rb') as f:
            content = base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        print(f'✗ {FILE} not found — run aggregator first')
        sys.exit(1)
    
    # Get current SHA if file exists
    r = requests.get(API_URL, headers=headers, timeout=10)
    sha = r.json().get('sha') if r.status_code == 200 else None
    
    # Push
    data = {
        'message': f'Update results {datetime.now().strftime("%H:%M:%S")}',
        'content': content
    }
    if sha:
        data['sha'] = sha
    
    r = requests.put(API_URL, headers=headers, json=data, timeout=30)
    
    if r.status_code in (200, 201):
        print(f'✓ Pushed {FILE} to GitHub at {datetime.now().strftime("%H:%M:%S")}')
        print(f'  Live at: https://mekcoleman.github.io/il-election-results/{FILE}')
    else:
        print(f'✗ Push failed: {r.status_code} — {r.json().get("message", "")}')
        sys.exit(1)

if __name__ == '__main__':
    push()
