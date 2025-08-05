#!/usr/bin/env python3
"""
Authentication service for Smart Chart RAG System
Google Cloud authentication functions
"""

import os
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from google.auth import default
from config.settings import GOOGLE_CONFIG

def generate_access_token():
    """Generate access token using service account credentials"""
    try:
        scopes = ["https://www.googleapis.com/auth/cloud-platform"]
        
        # Check if we're running in Cloud Run (use ADC) or locally (use service account file)
        if os.getenv('K_SERVICE'):  # Cloud Run environment
            # Use Application Default Credentials
            credentials, project = default(scopes=scopes)
        else:
            # Local development - use service account file
            credentials_path = GOOGLE_CONFIG['credentials_path']
            credentials = service_account.Credentials.from_service_account_file(
                credentials_path, scopes=scopes)
        
        credentials.refresh(Request())
        return credentials.token
    except Exception as e:
        print(f"❌ Error generating access token: {e}")
        return None 