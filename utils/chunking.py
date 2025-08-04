#!/usr/bin/env python3
"""
Chunking utilities for Smart Chart RAG System
Text chunking functions
"""

import re
from config.settings import CHUNKING_CONFIG

def hybrid_chunking(text, target_size=1500, max_size=1800, overlap=200):
    """
    Hybrid chunking strategy combining semantic and fixed-size chunking
    """
    if not text.strip():
        return []
    
    # Clean and normalize text
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Split by paragraphs first (semantic chunking)
    paragraphs = re.split(r'\n\s*\n', text)
    
    chunks = []
    current_chunk = ""
    
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue
        
        # If adding this paragraph would exceed max_size, finalize current chunk
        if len(current_chunk) + len(paragraph) > max_size and current_chunk:
            chunks.append(current_chunk.strip())
            
            # Start new chunk with overlap
            if overlap > 0 and len(current_chunk) > overlap:
                overlap_text = current_chunk[-overlap:]
                # Try to break at word boundary
                last_space = overlap_text.rfind(' ')
                if last_space > overlap // 2:
                    overlap_text = overlap_text[last_space + 1:]
                current_chunk = overlap_text + " " + paragraph
            else:
                current_chunk = paragraph
        else:
            if current_chunk:
                current_chunk += "\n\n" + paragraph
            else:
                current_chunk = paragraph
    
    # Add the last chunk if it exists
    if current_chunk.strip():
        chunks.append(current_chunk.strip())
    
    # Post-process chunks to ensure they meet size requirements
    final_chunks = []
    for chunk in chunks:
        if len(chunk) <= max_size:
            final_chunks.append(chunk)
        else:
            # Force split large chunks
            sub_chunks = force_split_chunk(chunk, max_size, overlap)
            final_chunks.extend(sub_chunks)
    
    return final_chunks

def force_split_chunk(chunk, max_size, overlap):
    """Force split a chunk that exceeds max_size"""
    if len(chunk) <= max_size:
        return [chunk]
    
    chunks = []
    start = 0
    
    while start < len(chunk):
        end = start + max_size
        
        # Try to break at word boundary
        if end < len(chunk):
            # Look for the last space within the last 100 characters
            search_start = max(start + max_size - 100, start)
            last_space = chunk.rfind(' ', search_start, end)
            
            if last_space > start + max_size // 2:
                end = last_space
        
        # Extract the chunk
        current_chunk = chunk[start:end].strip()
        if current_chunk:
            chunks.append(current_chunk)
        
        # Move start position with overlap
        if overlap > 0 and end < len(chunk):
            start = max(start + 1, end - overlap)
        else:
            start = end
    
    return chunks 