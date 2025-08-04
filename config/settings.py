#!/usr/bin/env python3
"""
Configuration settings for Smart Chart RAG System
Centralized configuration management
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database settings
DB_CONFIG = {
    'username': os.getenv('ORACLE_USERNAME'),
    'password': os.getenv('ORACLE_PASSWORD'),
    'host': os.getenv('ORACLE_HOST'),
    'port': int(os.getenv('ORACLE_PORT')),
    'service_name': os.getenv('ORACLE_SERVICE_NAME')
}

# Google Cloud settings
GOOGLE_CONFIG = {
    'project_id': os.getenv('VERTEX_PROJECT_ID'),
    'location': os.getenv('VERTEX_LOCATION'),
    'embedding_model': os.getenv('VERTEX_EMBEDDING_MODEL', 'text-embedding-005'),
    'credentials_path': os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 'gcp_secrets/llama-sa-key.json'),
    'llm_model': 'meta/llama-3.3-70b-instruct-maas'
}

# Chunking settings
CHUNKING_CONFIG = {
    'target_size': int(os.getenv('TARGET_CHUNK_SIZE', 1500)),
    'max_size': int(os.getenv('MAX_CHUNK_SIZE', 2000)),
    'overlap': int(os.getenv('OVERLAP_SIZE', 200)),
    'min_size': int(os.getenv('MIN_CHUNK_SIZE', 500)),
    'document_size_limit': int(os.getenv('DOCUMENT_SIZE_LIMIT', 250 * 1024))  # 250 KB
}

# API endpoints
API_ENDPOINTS = {
    'chat': f"https://{GOOGLE_CONFIG['location']}-aiplatform.googleapis.com/v1beta1/projects/{GOOGLE_CONFIG['project_id']}/locations/{GOOGLE_CONFIG['location']}/endpoints/openapi/chat/completions",
    'embeddings': f"https://{GOOGLE_CONFIG['location']}-aiplatform.googleapis.com/v1/projects/{GOOGLE_CONFIG['project_id']}/locations/{GOOGLE_CONFIG['location']}/publishers/google/models/{GOOGLE_CONFIG['embedding_model']}:predict"
}

# Streamlit settings
STREAMLIT_CONFIG = {
    'page_title': "Smart Chart RAG System",
    'page_icon': "🤖",
    'layout': "wide",
    'initial_sidebar_state': "expanded"
}

# Search settings
SEARCH_CONFIG = {
    'top_k': 8,
    'similarity_threshold': 0.7
} 