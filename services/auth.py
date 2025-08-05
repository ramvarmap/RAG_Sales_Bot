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
        
        # Check if we're running in Cloud Run or GCP environment
        is_cloud_run = (
            os.getenv('K_SERVICE') or  # Cloud Run
            os.getenv('K_REVISION') or  # Cloud Run
            os.getenv('GOOGLE_CLOUD_PROJECT') or  # GCP environment
            os.getenv('GCP_PROJECT')  # Alternative GCP project env var
        )
        
        if is_cloud_run:
            # Use Application Default Credentials in Cloud Run/GCP
            print("🔧 Using Application Default Credentials for Cloud Run")
            credentials, project = default(scopes=scopes)
        else:
            # Local development - use service account file
            print("🔧 Using service account file for local development")
            credentials_path = GOOGLE_CONFIG['credentials_path']
            
            # Check if file exists
            if not os.path.exists(credentials_path):
                print(f"⚠️ Service account file not found: {credentials_path}")
                print("🔄 Falling back to Application Default Credentials")
                credentials, project = default(scopes=scopes)
            else:
                credentials = service_account.Credentials.from_service_account_file(
                    credentials_path, scopes=scopes)
        
        credentials.refresh(Request())
        print("✅ Access token generated successfully")
        return credentials.token
    except Exception as e:
        print(f"❌ Error generating access token: {e}")
        return None 