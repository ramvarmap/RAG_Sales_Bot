#!/usr/bin/env python3
"""
LLM service for Smart Chart RAG System
LLM interaction functions
"""

import requests
from config.settings import API_ENDPOINTS, GOOGLE_CONFIG

def generate_llama_response(question, context, access_token):
    """Generate LLM response using Llama 3.3-70B"""
    try:
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Create context-aware prompt
        prompt = f"""You are a helpful AI assistant. Use the following context to answer the user's question.

Context:
{context}

Question: {question}

Please provide a comprehensive answer based on the context provided. If the context doesn't contain enough information to answer the question, please say so. Always cite the source documents when possible.

Answer:"""
        
        data = {
            "model": GOOGLE_CONFIG['llm_model'],
            "stream": False,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ],
            "max_tokens": 500,
            "temperature": 0.7
        }
        
        response = requests.post(API_ENDPOINTS['chat'], headers=headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0].get('message', {}).get('content', '')
                return content
            else:
                return "❌ No response generated from LLM"
        else:
            return f"❌ Error generating LLM response: {response.status_code} - {response.text}"
            
    except Exception as e:
        return f"❌ Error generating LLM response: {e}" 