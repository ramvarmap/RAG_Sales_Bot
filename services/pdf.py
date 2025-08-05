#!/usr/bin/env python3
"""
PDF service for Smart Chart RAG System
PDF processing functions
"""

import PyPDF2
import streamlit as st
from config.settings import CHUNKING_CONFIG


def extract_text_from_pdf(pdf_file):
    """Extract text from PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        pages_data = []

        for page_num, page in enumerate(pdf_reader.pages):
            page_text = page.extract_text()
            if page_text.strip():
                pages_data.append((page_num, page_text))

        return pages_data
    except Exception as e:
        if "st" in globals():
            st.error(f"❌ Error extracting text from PDF: {e}")
        else:
            print(f"❌ Error extracting text from PDF: {e}")
        return []


def validate_document_requirements(pdf_file):
    """Validate PDF document requirements"""
    try:
        # Check file size
        pdf_file.seek(0, 2)  # Seek to end
        file_size = pdf_file.tell()
        pdf_file.seek(0)  # Reset to beginning

        if file_size > CHUNKING_CONFIG["document_size_limit"]:
            return (
                False,
                f"File size ({file_size / 1024:.1f} KB) exceeds limit ({CHUNKING_CONFIG['document_size_limit'] / 1024} KB)",
            )

        # Check if PDF has selectable text
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        total_text = ""

        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                total_text += page_text

        if len(total_text.strip()) < 100:  # Minimum text requirement
            return (
                False,
                "PDF appears to have no selectable text or insufficient content",
            )

        return True, "PDF meets all requirements"

    except Exception as e:
        return False, f"Error validating PDF: {e}"
