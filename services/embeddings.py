#!/usr/bin/env python3
"""
Embeddings service for Smart Chart RAG System
Embedding generation functions
"""

import requests
from config.settings import API_ENDPOINTS


def generate_embeddings(text, access_token):
    """Generate embeddings for text"""
    try:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        data = {"instances": [{"content": text}]}

        response = requests.post(
            API_ENDPOINTS["embeddings"], headers=headers, json=data
        )

        if response.status_code == 200:
            result = response.json()
            return result["predictions"][0]["embeddings"]["values"]
        else:
            print(
                f"❌ Error generating embeddings: {response.status_code} - {response.text}"
            )
            return None

    except Exception as e:
        print(f"❌ Error generating embeddings: {e}")
        return None


def generate_embeddings_for_query(query, access_token):
    """Generate embeddings for the search query"""
    return generate_embeddings(query, access_token)
