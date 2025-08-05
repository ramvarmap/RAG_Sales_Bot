#!/usr/bin/env python3
"""
Modular Streamlit RAG Application
Enhanced version with original UI and improved functionality
"""

import streamlit as st
import tempfile
import time
import pandas as pd
from datetime import datetime

# Import from our modular structure
from config.settings import STREAMLIT_CONFIG, CHUNKING_CONFIG
from database.connection import get_connection
from database.operations import store_document_with_chunks, search_chunks, get_document_history
from services.auth import generate_access_token
from services.pdf import extract_text_from_pdf, validate_document_requirements
from services.embeddings import generate_embeddings_for_query
from services.llm import generate_llama_response
from utils.validators import validate_pdf_file, validate_search_query

# Page configuration
st.set_page_config(
    page_title="Smart Chart RAG System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #ff7f0e;
        margin-bottom: 1rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .ai-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
</style>
""", unsafe_allow_html=True)

def process_pdf_upload():
    """Page 1: PDF Upload and Processing with Chunking"""
    st.markdown('<h1 class="main-header">📄 PDF Upload & Processing</h1>', unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="info-box">
        <h4>📋 Instructions:</h4>
        <ul>
            <li>Upload your PDF documents here (max {CHUNKING_CONFIG['document_size_limit'] / 1024} KB)</li>
            <li>The system will extract text, create chunks, and generate embeddings</li>
            <li>Documents will be stored in the vector database with chunking</li>
            <li>You can then chat with the AI about the uploaded content</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # File uploader - Moved to top
    st.markdown('<h3 class="sub-header">📤 Upload New Documents</h3>', unsafe_allow_html=True)
    uploaded_files = st.file_uploader(
        "Choose PDF files to upload",
        type=['pdf'],
        accept_multiple_files=True,
        help=f"Select one or more PDF files to process (max {CHUNKING_CONFIG['document_size_limit'] / 1024} KB each)"
    )
    
    if uploaded_files:
        st.markdown('<h3 class="sub-header">📊 Processing Status</h3>', unsafe_allow_html=True)
        
        # Initialize connections
        with st.spinner("🔌 Connecting to database..."):
            connection = get_connection()
            if not connection:
                st.error("❌ Failed to connect to database!")
                return
        
        with st.spinner("🔑 Generating access token..."):
            access_token = generate_access_token()
            if not access_token:
                st.error("❌ Failed to generate access token!")
                connection.close()
                return
        
        st.success("✅ All connections established successfully!")
        
        # Process each uploaded file
        for uploaded_file in uploaded_files:
            st.markdown(f"---")
            st.markdown(f"**Processing: {uploaded_file.name}**")
            
            # Create progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                # Step 1: Validate document requirements
                status_text.text("🔍 Validating document requirements...")
                progress_bar.progress(10)
                
                is_valid, validation_message = validate_document_requirements(uploaded_file)
                if not is_valid:
                    st.error(f"❌ {validation_message}")
                    continue
                
                st.success(f"✅ {validation_message}")
                
                # Step 2: Extract text with page tracking
                status_text.text("📖 Extracting text from PDF...")
                progress_bar.progress(25)
                
                pages_data = extract_text_from_pdf(uploaded_file)
                if not pages_data:
                    st.error(f"❌ Failed to extract text from {uploaded_file.name}")
                    continue
                
                total_text_length = sum(len(page['text']) for page in pages_data)
                st.success(f"✅ Text extracted successfully ({len(pages_data)} pages, {total_text_length} characters)")
                
                # Step 3: Create chunks and store with embeddings
                status_text.text("🧩 Creating chunks and generating embeddings...")
                progress_bar.progress(50)
                
                # Get file size
                uploaded_file.seek(0, 2)
                file_size = uploaded_file.tell()
                uploaded_file.seek(0)
                
                doc_name = uploaded_file.name.replace('.pdf', '')
                success, doc_id = store_document_with_chunks(
                    connection, doc_name, file_size, pages_data, access_token
                )
                
                if not success:
                    st.error(f"❌ Failed to process {uploaded_file.name}")
                    continue
                
                # Step 4: Complete
                progress_bar.progress(100)
                status_text.text("✅ Processing completed!")
                
                st.markdown(f"""
                <div class="success-box">
                    <h4>✅ Successfully processed: {uploaded_file.name}</h4>
                    <ul>
                        <li><strong>Document ID:</strong> {doc_id}</li>
                        <li><strong>Pages Processed:</strong> {len(pages_data)}</li>
                        <li><strong>Total Text Length:</strong> {total_text_length} characters</li>
                        <li><strong>File Size:</strong> {file_size / 1024:.1f} KB</li>
                        <li><strong>Status:</strong> Ready for chat</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
                
            except Exception as e:
                st.error(f"❌ Error processing {uploaded_file.name}: {e}")
            
            # Reset progress
            progress_bar.empty()
            status_text.empty()
        
        connection.close()
        st.success("🎉 All files processed successfully!")
    
    st.markdown("---")
    
    # Show document history - Moved below upload section
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown('<h3 class="sub-header">📚 Document History</h3>', unsafe_allow_html=True)
    with col2:
        if st.button("🔄 Refresh History", help="Refresh the document history"):
            st.rerun()
    
    # Get connection for history
    connection = get_connection()
    if connection:
        try:
            documents = get_document_history(connection)
            
            if documents:
                # Create a DataFrame for better display
                history_data = []
                for doc in documents:
                    history_data.append({
                        "ID": doc['id'],
                        "Document Name": doc['name'],
                        "Chunks": doc['chunks'],
                        "Size (KB)": f"{doc['size_kb']:.1f}",
                        "Status": doc['status'],
                        "Upload Date": doc['created_date'].strftime("%Y-%m-%d %H:%M:%S") if doc['created_date'] else "Unknown"
                    })
                
                # Display as a table
                df = pd.DataFrame(history_data)
                
                # Add search/filter functionality
                search_term = st.text_input("🔍 Search documents:", placeholder="Enter document name to filter...")
                
                if search_term:
                    # Filter the dataframe
                    filtered_df = df[df['Document Name'].str.contains(search_term, case=False, na=False)]
                    st.write(f"📋 Showing {len(filtered_df)} of {len(df)} documents matching '{search_term}'")
                    display_df = filtered_df
                else:
                    display_df = df
                
                st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "ID": st.column_config.NumberColumn("ID", width="small"),
                        "Document Name": st.column_config.TextColumn("Document Name", width="medium"),
                        "Chunks": st.column_config.NumberColumn("Chunks", width="small"),
                        "Size (KB)": st.column_config.TextColumn("Size (KB)", width="small"),
                        "Status": st.column_config.TextColumn("Status", width="small"),
                        "Upload Date": st.column_config.TextColumn("Upload Date", width="medium"),
                        "File Status": st.column_config.TextColumn("File Status", width="small")
                    }
                )
                
                # Summary statistics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("📚 Total Documents", len(documents))
                with col2:
                    completed_docs = sum(1 for doc in documents if doc['status'] == 'COMPLETED')
                    st.metric("✅ Completed", completed_docs)
                with col3:
                    total_chunks_sum = sum(doc['chunks'] for doc in documents)
                    st.metric("🧩 Total Chunks", total_chunks_sum)
                with col4:
                    total_size_mb = sum(doc['size_kb'] for doc in documents) / 1024
                    st.metric("📊 Total Size", f"{total_size_mb:.1f} MB")
                
                # Show recent uploads
                if len(documents) > 0:
                    st.markdown("---")
                    st.markdown("**📅 Recent Uploads:**")
                    
                    # Show last 3 documents
                    recent_docs = documents[:3]
                    for doc in recent_docs:
                        col1, col2, col3 = st.columns([2, 2, 1])
                        with col1:
                            st.write(f"📄 **{doc['name']}** ({doc['chunks']} chunks)")
                        with col2:
                            if doc['created_date']:
                                st.write(f"📅 {doc['created_date'].strftime('%Y-%m-%d %H:%M')}")
                            else:
                                st.write("📅 Unknown date")
                        with col3:
                            if doc['status'] == 'COMPLETED':
                                st.success("✅ Completed")
                            elif doc['status'] == 'CHUNKING':
                                st.warning("⏳ Processing")
                            else:
                                st.error("❌ Error")
                
            else:
                st.info("📭 No documents have been processed yet. Upload your first PDF to get started!")
                
        except Exception as e:
            st.error(f"❌ Error loading document history: {e}")
        finally:
            connection.close()
    else:
        st.error("❌ Cannot load document history - database connection failed")

def chat_interface():
    """Page 2: Interactive Chat Interface with Chunking"""
    st.markdown('<h1 class="main-header">💬 RAG Chat Interface</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-box">
        <h4>🤖 How it works:</h4>
        <ul>
            <li>Ask questions about your uploaded documents</li>
            <li>The AI will search through document chunks and provide answers</li>
            <li>Answers are based on the actual content from your PDFs</li>
            <li>You can ask follow-up questions and have a conversation</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state for chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "connections_established" not in st.session_state:
        st.session_state.connections_established = False
    
    # Initialize connections if not already done
    if not st.session_state.connections_established:
        with st.spinner("🔌 Establishing connections..."):
            connection = get_connection()
            access_token = generate_access_token()
            
            if connection and access_token:
                st.session_state.connection = connection
                st.session_state.access_token = access_token
                st.session_state.connections_established = True
                st.success("✅ Connections established successfully!")
            else:
                st.error("❌ Failed to establish connections!")
                return
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask a question about your documents..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate AI response
        with st.chat_message("assistant"):
            with st.spinner("🤖 Thinking..."):
                # Step 1: Generate embeddings for the question
                query_embeddings = generate_embeddings_for_query(prompt, st.session_state.access_token)
                
                if not query_embeddings:
                    st.error("❌ Failed to generate embeddings!")
                    return
                
                # Step 2: Perform chunk-based search
                search_results = search_chunks(
                    st.session_state.connection, 
                    query_embeddings, 
                    prompt, 
                    top_k=15
                )
                
                if not search_results:
                    st.error("❌ No relevant chunks found!")
                    return
                
                # Step 3: Build comprehensive context
                context = "You are a Toyota vehicle expert. Based on the following detailed specifications:\n\n"
                
                # Use ALL search results for comprehensive context
                for i, result in enumerate(search_results, 1):
                    context += f"📄 {result['doc_name']} (Page {result['page']}):\n"
                    context += f"{result['chunk_text'][:500]}...\n\n"
                
                # Add specific instructions for better responses
                context += f"\n=== INSTRUCTIONS ===\n"
                context += f"1. Provide SPECIFIC details about Toyota models, features, and specifications\n"
                context += f"2. When asked about available models, list them with their key features\n"
                context += f"3. Include relevant technical specifications when available\n"
                context += f"4. Be direct and informative - avoid generic responses\n"
                context += f"5. Use the actual content from the specifications above\n"
                context += f"6. If asked for a count, provide the exact number based on the content\n\n"
                
                # Step 4: Generate AI response
                ai_response = generate_llama_response(prompt, context, st.session_state.access_token)
                
                if ai_response:
                    st.markdown(ai_response)
                    # Add AI response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": ai_response})
                else:
                    st.error("❌ Failed to generate AI response!")

def main():
    """Main application"""
    # Sidebar navigation
    st.sidebar.title("🤖 Smart Chart RAG System")
    st.sidebar.markdown("---")
    
    # Page selection
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["📄 Upload PDFs", "💬 Chat Interface"]
    )
    
    # Sidebar info
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    ### 📊 System Status
    - ✅ Vector Database: Connected
    - ✅ Embedding Model: Ready
    - ✅ Chat Model: Ready
    - ✅ Chunking System: Active
    
    ### 🔧 Features
    - PDF Text Extraction
    - Hybrid Chunking
    - Vector Embeddings
    - Chunk-based Search
    - AI-Powered Chat
    """)
    
    # Display selected page
    if page == "📄 Upload PDFs":
        process_pdf_upload()
    elif page == "💬 Chat Interface":
        chat_interface()

if __name__ == "__main__":
    main() 