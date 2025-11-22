#!/usr/bin/env python3
"""
Test script for background token refresh functionality
"""

import requests
import time
import json

def test_token_refresh_hint():
    """Test that refresh hint headers are sent when token is near expiry"""
    base_url = "http://localhost:5000"
    
    # Login to get tokens
    login_response = requests.post(f"{base_url}/auth/login", json={
        "username": "testuser",
        "password": "password123"
    })
    
    if login_response.status_code != 200:
        print("❌ Login failed")
        return
    
    tokens = login_response.json()
    access_token = tokens['access_token']
    
    print("✅ Login successful")
    
    # Call protected endpoint
    protected_response = requests.get(f"{base_url}/api/protected", 
                                    headers={"Authorization": f"Bearer {access_token}"})
    
    if protected_response.status_code == 200:
        print("✅ Protected endpoint accessible")
        
        # Check for refresh hint header
        refresh_hint = protected_response.headers.get('X-Token-Refresh-Needed')
        if refresh_hint == 'true':
            print("✅ Refresh hint header present")
        else:
            print("ℹ️  No refresh hint (token not near expiry)")
    else:
        print("❌ Protected endpoint failed")

if __name__ == "__main__":
    test_token_refresh_hint()