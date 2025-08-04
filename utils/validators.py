#!/usr/bin/env python3
"""
Validators for Smart Chart RAG System
Input validation functions
"""

import os
from config.settings import CHUNKING_CONFIG

def validate_pdf_file(pdf_file):
    """Validate PDF file requirements"""
    try:
        # Check file size
        pdf_file.seek(0, 2)  # Seek to end
        file_size = pdf_file.tell()
        pdf_file.seek(0)  # Reset to beginning
        
        if file_size > CHUNKING_CONFIG['document_size_limit']:
            return False, f"File size ({file_size / 1024:.1f} KB) exceeds limit ({CHUNKING_CONFIG['document_size_limit'] / 1024} KB)"
        
        # Check file extension
        if not pdf_file.name.lower().endswith('.pdf'):
            return False, "File must be a PDF"
        
        return True, "PDF file is valid"
        
    except Exception as e:
        return False, f"Error validating file: {e}"

def validate_search_query(query):
    """Validate search query"""
    if not query or not query.strip():
        return False, "Search query cannot be empty"
    
    if len(query.strip()) < 3:
        return False, "Search query must be at least 3 characters long"
    
    return True, "Search query is valid"

def validate_database_connection(connection):
    """Validate database connection"""
    if connection is None:
        return False, "Database connection failed"
    
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT 1 FROM DUAL")
        cursor.fetchone()
        cursor.close()
        return True, "Database connection is valid"
    except Exception as e:
        return False, f"Database connection error: {e}" 