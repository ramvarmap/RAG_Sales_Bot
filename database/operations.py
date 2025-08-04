#!/usr/bin/env python3
"""
Database operations for Smart Chart RAG System
All database-related functions centralized here
"""

import oracledb
import streamlit as st
import os
from config.settings import DB_CONFIG
from .connection import get_connection

def create_tables():
    """Create all required database tables"""
    try:
        connection = get_connection()
        if not connection:
            return False
            
        cursor = connection.cursor()
        
        print("📋 Creating DOCUMENTS table...")
        cursor.execute("""
            CREATE TABLE DOCUMENTS (
                id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                doc_name VARCHAR2(255) NOT NULL,
                total_size_bytes NUMBER,
                total_chunks NUMBER DEFAULT 0,
                chunking_status VARCHAR2(20) DEFAULT 'PENDING',
                upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        print("📋 Creating DOCUMENT_CHUNKS table...")
        cursor.execute("""
            CREATE TABLE DOCUMENT_CHUNKS (
                id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                doc_id NUMBER NOT NULL,
                chunk_index NUMBER NOT NULL,
                chunk_text CLOB,
                chunk_size_chars NUMBER,
                page_number NUMBER,
                embeddings VECTOR(768),
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_doc_chunks_doc_id FOREIGN KEY (doc_id) REFERENCES DOCUMENTS(id),
                CONSTRAINT chk_chunk_size CHECK (chunk_size_chars <= 3000)
            )
        """)
        
        print("📋 Creating CHUNKING_METADATA table...")
        cursor.execute("""
            CREATE TABLE CHUNKING_METADATA (
                id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                doc_id NUMBER NOT NULL,
                chunking_strategy VARCHAR2(50) DEFAULT 'HYBRID',
                target_chunk_size NUMBER DEFAULT 1500,
                max_chunk_size NUMBER DEFAULT 2000,
                overlap_size NUMBER DEFAULT 200,
                total_chunks_created NUMBER DEFAULT 0,
                processing_time_ms NUMBER,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_chunking_meta_doc_id FOREIGN KEY (doc_id) REFERENCES DOCUMENTS(id)
            )
        """)
        
        print("📋 Creating indexes...")
        cursor.execute("CREATE INDEX idx_documents_doc_name ON DOCUMENTS(doc_name)")
        cursor.execute("CREATE INDEX idx_documents_upload_date ON DOCUMENTS(upload_date)")
        cursor.execute("CREATE INDEX idx_documents_status ON DOCUMENTS(chunking_status)")
        cursor.execute("CREATE INDEX idx_chunks_doc_id ON DOCUMENT_CHUNKS(doc_id)")
        cursor.execute("CREATE INDEX idx_chunks_page_number ON DOCUMENT_CHUNKS(page_number)")
        cursor.execute("CREATE INDEX idx_chunks_chunk_index ON DOCUMENT_CHUNKS(chunk_index)")
        
        connection.commit()
        cursor.close()
        connection.close()
        
        print("✅ All tables and indexes created successfully!")
        return True
        
    except Exception as e:
        if connection:
            connection.rollback()
            connection.close()
        print(f"❌ Error creating tables: {e}")
        return False

def store_document_with_chunks(connection, doc_name, file_size, pages_data, access_token):
    """Store document and chunks in database"""
    try:
        cursor = connection.cursor()
        
        # Insert document record
        var_id = cursor.var(int)
        cursor.execute("""
            INSERT INTO DOCUMENTS (doc_name, total_size_bytes, chunking_status)
            VALUES (:1, :2, 'CHUNKING')
            RETURNING id INTO :3
        """, (doc_name, file_size, var_id))
        
        document_id = var_id.getvalue()
        
        # Process each page and create chunks
        total_chunks = 0
        for page_num, page_text in pages_data:
            if not page_text.strip():
                continue
                
            # Create chunks for this page
            chunks = hybrid_chunking(page_text)
            
            for chunk_index, chunk_text in enumerate(chunks):
                # Generate embeddings for chunk
                chunk_embeddings = generate_embeddings(chunk_text, access_token)
                if not chunk_embeddings:
                    continue
                
                # Store chunk with embeddings
                chunk_embeddings_json = '[' + ','.join(map(str, chunk_embeddings)) + ']'
                
                cursor.execute("""
                    DECLARE
                        v_embeddings VECTOR(768);
                    BEGIN
                        v_embeddings := TO_VECTOR(:1);
                        INSERT INTO DOCUMENT_CHUNKS 
                        (doc_id, chunk_index, chunk_text, chunk_size_chars, page_number, embeddings)
                        VALUES (:2, :3, :4, :5, :6, v_embeddings);
                    END;
                """, (chunk_embeddings_json, document_id, chunk_index, chunk_text, len(chunk_text), page_num + 1))
                
                total_chunks += 1
        
        # Update document with final chunk count and status
        cursor.execute("""
            UPDATE DOCUMENTS 
            SET total_chunks = :1, chunking_status = 'COMPLETED'
            WHERE id = :2
        """, (total_chunks, document_id))
        
        connection.commit()
        return True, document_id
        
    except Exception as e:
        connection.rollback()
        if 'st' in globals():
            st.error(f"❌ Error storing document and chunks: {e}")
        else:
            print(f"❌ Error storing document and chunks: {e}")
        return False, None

def search_chunks(connection, query_embeddings, search_query, top_k=15):
    """Search for relevant chunks using vector similarity"""
    try:
        cursor = connection.cursor()
        
        query_embeddings_json = '[' + ','.join(map(str, query_embeddings)) + ']'
        
        cursor.execute("""
            SELECT 
                dc.id,
                dc.doc_id,
                dc.chunk_index,
                dc.chunk_size_chars,
                dc.page_number,
                d.doc_name,
                dc.chunk_text,
                dc.embeddings <-> TO_VECTOR(:1) as similarity
            FROM DOCUMENT_CHUNKS dc
            JOIN DOCUMENTS d ON dc.doc_id = d.id
            WHERE d.chunking_status = 'COMPLETED'
            ORDER BY similarity
            FETCH FIRST :2 ROWS ONLY
        """, (query_embeddings_json, top_k))
        
        results = []
        for row in cursor.fetchall():
            chunk_id, doc_id, chunk_index, size, page, doc_name, chunk_text, similarity = row
            # Convert CLOB to string if needed
            if hasattr(chunk_text, 'read'):
                chunk_text = chunk_text.read()
            elif chunk_text is None:
                chunk_text = ""
            
            results.append({
                'chunk_id': chunk_id,
                'doc_id': doc_id,
                'chunk_index': chunk_index,
                'size': size,
                'page': page,
                'doc_name': doc_name,
                'chunk_text': chunk_text,
                'similarity': similarity
            })
        
        return results
        
    except Exception as e:
        if 'st' in globals():
            st.error(f"❌ Error searching chunks: {e}")
        else:
            print(f"❌ Error searching chunks: {e}")
        return []

def get_document_history(connection):
    """Get document processing history"""
    try:
        cursor = connection.cursor()
        
        cursor.execute("""
            SELECT id, doc_name, total_chunks, total_size_bytes, 
                   chunking_status, created_date
            FROM DOCUMENTS 
            ORDER BY created_date DESC
        """)
        
        documents = []
        for row in cursor.fetchall():
            doc_id, doc_name, total_chunks, total_size, status, created_date = row
            
            # Calculate file size in KB
            size_kb = round(total_size / 1024, 1) if total_size else 0
            
            # Check if PDF file exists
            pdf_path = f"analysis/{doc_name}"
            pdf_available = "✅ Available" if os.path.exists(pdf_path) else "❌ Missing"
            
            documents.append({
                'id': doc_id,
                'name': doc_name,
                'chunks': total_chunks,
                'size_kb': size_kb,
                'status': status,
                'created_date': created_date,
                'pdf_available': pdf_available
            })
        
        return documents
        
    except Exception as e:
        if 'st' in globals():
            st.error(f"❌ Error getting document history: {e}")
        else:
            print(f"❌ Error getting document history: {e}")
        return []

# Import required functions from other modules
from utils.chunking import hybrid_chunking
from services.embeddings import generate_embeddings 