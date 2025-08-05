#!/usr/bin/env python3
"""
Modular CLI RAG Application
Simplified command-line interface using the new modular structure
"""

import os
import sys

# Import from our modular structure
from database.connection import get_connection
from database.operations import search_chunks, get_document_history
from services.auth import generate_access_token
from services.embeddings import generate_embeddings_for_query
from services.llm import generate_llama_response
from utils.validators import validate_search_query


def display_welcome():
    """Display welcome message"""
    print("🚀 Smart Chart RAG System - CLI")
    print("=" * 50)
    print("💡 Ask questions about Toyota vehicles and get AI-powered answers!")
    print("💡 Type 'quit' or 'exit' to end the session")
    print("💡 Type 'list' to see available documents")
    print("=" * 50)


def initialize_connections():
    """Initialize database and API connections"""
    print("🔌 Initializing connections...")

    # Test database connection
    connection = get_connection()
    if not connection:
        print("❌ Failed to connect to database!")
        return None, None

    # Generate access token
    access_token = generate_access_token()
    if not access_token:
        print("❌ Failed to generate access token!")
        connection.close()
        return None, None

    print("✅ All connections established successfully!")
    return connection, access_token


def list_documents(connection):
    """List all available documents"""
    print("\n📋 Available Documents:")
    print("-" * 50)

    documents = get_document_history(connection)
    if not documents:
        print("📭 No documents found. Please upload some PDFs first!")
        return

    for i, doc in enumerate(documents, 1):
        print(f"{i}. {doc['name']} (ID: {doc['id']})")
        print(
            f"   Chunks: {doc['chunks']}, Size: {doc['size_kb']} KB, Status: {doc['status']}"
        )
        print(f"   Created: {doc['created_date']}")
        print()


def process_query(connection, access_token, query):
    """Process a user query"""
    print(f"\n🔍 Searching for: '{query}'")
    print("-" * 50)

    # Validate query
    is_valid, message = validate_search_query(query)
    if not is_valid:
        print(f"❌ {message}")
        return

    # Generate embeddings for query
    print("1️⃣ Generating embeddings...")
    query_embeddings = generate_embeddings_for_query(query, access_token)
    if not query_embeddings:
        print("❌ Failed to generate embeddings for query!")
        return

    # Search for relevant chunks
    print("2️⃣ Searching documents...")
    search_results = search_chunks(connection, query_embeddings, query)

    if not search_results:
        print("❌ No relevant documents found!")
        return

    print(f"🔍 Found {len(search_results)} relevant documents:")
    for i, result in enumerate(search_results, 1):
        print(f"   {i}. {result['doc_name']} (Score: {result['similarity']:.2f})")

    # Build context from search results
    print("3️⃣ Generating AI response...")
    context = "You are a Toyota vehicle expert. Based on the following detailed specifications:\n\n"

    # Use ALL search results for comprehensive context
    for i, result in enumerate(search_results, 1):
        context += f"📄 {result['doc_name']} (Page {result['page']}):\n"
        context += f"{result['chunk_text'][:500]}...\n\n"

    # Add specific instructions for better responses
    context += f"\n=== INSTRUCTIONS ===\n"
    context += f"1. Provide SPECIFIC details about Toyota models, features, and specifications\n"
    context += (
        f"2. When asked about available models, list them with their key features\n"
    )
    context += f"3. Include relevant technical specifications when available\n"
    context += f"4. Be direct and informative - avoid generic responses\n"
    context += f"5. Use the actual content from the specifications above\n"
    context += (
        f"6. If asked for a count, provide the exact number based on the content\n\n"
    )

    # Generate LLM response
    response = generate_llama_response(query, context, access_token)

    print("\n🤖 AI Answer:")
    print("=" * 50)
    print(response)
    print("=" * 50)


def interactive_chat():
    """Interactive chat loop"""
    display_welcome()

    # Initialize connections
    connection, access_token = initialize_connections()
    if not connection or not access_token:
        print("❌ Failed to initialize connections. Exiting...")
        return

    print("\n" + "=" * 50)

    try:
        while True:
            # Get user input
            user_input = input("\n🤔 Your question: ").strip()

            # Check for exit commands
            if user_input.lower() in ["quit", "exit", "q"]:
                print("👋 Chat session ended. Goodbye!")
                break

            # Check for list command
            if user_input.lower() == "list":
                list_documents(connection)
                continue

            # Skip empty input
            if not user_input:
                continue

            # Process the query
            process_query(connection, access_token, user_input)

    except KeyboardInterrupt:
        print("\n\n👋 Chat session interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    finally:
        # Clean up connections
        if connection:
            connection.close()
        print("🔌 Connections closed.")


def main():
    """Main function"""
    try:
        interactive_chat()
    except Exception as e:
        print(f"❌ Application error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
