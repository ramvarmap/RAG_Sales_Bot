#!/usr/bin/env python3
"""
Test Models for Smart Chart RAG System
Comprehensive testing of all system components
"""

import os
import sys
import time
from datetime import datetime


def print_header():
    """Print test header"""
    print("=" * 60)
    print("🧪 Smart Chart RAG System - Component Tests")
    print("=" * 60)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()


def test_imports():
    """Test if all modules can be imported"""
    print("🔍 Testing module imports...")

    try:
        from config.settings import DB_CONFIG, GOOGLE_CONFIG, CHUNKING_CONFIG

        print("✅ Configuration module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import configuration: {e}")
        return False

    try:
        from database.connection import get_connection, test_connection

        print("✅ Database connection module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import database module: {e}")
        return False

    try:
        from database.operations import (
            create_tables,
            search_chunks,
            get_document_history,
        )

        print("✅ Database operations module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import database operations: {e}")
        return False

    try:
        from services.auth import generate_access_token

        print("✅ Authentication service imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import auth service: {e}")
        return False

    try:
        from services.embeddings import generate_embeddings_for_query

        print("✅ Embeddings service imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import embeddings service: {e}")
        return False

    try:
        from services.llm import generate_llama_response

        print("✅ LLM service imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import LLM service: {e}")
        return False

    try:
        from services.pdf import extract_text_from_pdf, validate_document_requirements

        print("✅ PDF service imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import PDF service: {e}")
        return False

    try:
        from utils.chunking import hybrid_chunking

        print("✅ Chunking utilities imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import chunking utilities: {e}")
        return False

    try:
        from utils.validators import validate_pdf_file, validate_search_query

        print("✅ Validators imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import validators: {e}")
        return False

    return True


def test_configuration():
    """Test configuration loading"""
    print("\n⚙️ Testing configuration...")

    try:
        from config.settings import DB_CONFIG, GOOGLE_CONFIG, CHUNKING_CONFIG

        # Test database config
        required_db_keys = ["username", "password", "host", "port", "service_name"]
        for key in required_db_keys:
            if key not in DB_CONFIG:
                print(f"❌ Missing database config key: {key}")
                return False

        # Test Google config
        required_google_keys = [
            "project_id",
            "location",
            "embedding_model",
            "credentials_path",
        ]
        for key in required_google_keys:
            if key not in GOOGLE_CONFIG:
                print(f"❌ Missing Google config key: {key}")
                return False

        # Test chunking config
        required_chunking_keys = [
            "target_size",
            "max_size",
            "overlap",
            "min_size",
            "document_size_limit",
        ]
        for key in required_chunking_keys:
            if key not in CHUNKING_CONFIG:
                print(f"❌ Missing chunking config key: {key}")
                return False

        print("✅ Configuration loaded successfully")
        return True

    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


def test_database_connection():
    """Test database connection"""
    print("\n🗄️ Testing database connection...")

    try:
        from database.connection import test_connection

        success, message = test_connection()
        if success:
            print("✅ Database connection successful")
            return True
        else:
            print(f"❌ Database connection failed: {message}")
            return False

    except Exception as e:
        print(f"❌ Database connection test failed: {e}")
        return False


def test_google_authentication():
    """Test Google Cloud authentication"""
    print("\n🔑 Testing Google Cloud authentication...")

    try:
        from services.auth import generate_access_token

        # Check if service account key exists
        from config.settings import GOOGLE_CONFIG

        key_path = GOOGLE_CONFIG["credentials_path"]

        if not os.path.exists(key_path):
            print(f"❌ Service account key not found: {key_path}")
            print(
                "   Please place your Google service account JSON key at this location"
            )
            return False

        # Generate access token
        token = generate_access_token()
        if token:
            print("✅ Google Cloud authentication successful")
            return True
        else:
            print("❌ Failed to generate access token")
            return False

    except Exception as e:
        print(f"❌ Google authentication test failed: {e}")
        return False


def test_embedding_generation():
    """Test embedding generation"""
    print("\n🧠 Testing embedding generation...")

    try:
        from services.auth import generate_access_token
        from services.embeddings import generate_embeddings_for_query

        # Get access token
        token = generate_access_token()
        if not token:
            print("❌ Cannot test embeddings without access token")
            return False

        # Test embedding generation
        test_query = "Toyota Corolla specifications"
        embeddings = generate_embeddings_for_query(test_query, token)

        if embeddings and len(embeddings) > 0:
            print(
                f"✅ Embedding generation successful (vector size: {len(embeddings)})"
            )
            return True
        else:
            print("❌ Failed to generate embeddings")
            return False

    except Exception as e:
        print(f"❌ Embedding generation test failed: {e}")
        return False


def test_llm_generation():
    """Test LLM response generation"""
    print("\n🤖 Testing LLM response generation...")

    try:
        from services.auth import generate_access_token
        from services.llm import generate_llama_response

        # Get access token
        token = generate_access_token()
        if not token:
            print("❌ Cannot test LLM without access token")
            return False

        # Test LLM response
        test_question = "What is the fuel efficiency of Toyota Corolla?"
        test_context = "The Toyota Corolla has excellent fuel efficiency with EPA ratings of 32 city/41 highway mpg."

        response = generate_llama_response(test_question, test_context, token)

        if response and not response.startswith("❌"):
            print("✅ LLM response generation successful")
            print(f"   Response preview: {response[:100]}...")
            return True
        else:
            print(f"❌ LLM response generation failed: {response}")
            return False

    except Exception as e:
        print(f"❌ LLM generation test failed: {e}")
        return False


def test_chunking():
    """Test text chunking functionality"""
    print("\n✂️ Testing text chunking...")

    try:
        from utils.chunking import hybrid_chunking

        # Test text
        test_text = """
        This is a test document about Toyota vehicles. The Toyota Corolla is a compact car that offers excellent fuel efficiency.
        
        The Corolla comes with various engine options including a 1.8L 4-cylinder engine and a hybrid powertrain.
        
        Safety features include Toyota Safety Sense 2.0 with pre-collision system, lane departure alert, and adaptive cruise control.
        
        The interior is well-designed with comfortable seating and modern technology features including Apple CarPlay and Android Auto.
        """

        chunks = hybrid_chunking(test_text, target_size=150, max_size=200, overlap=50)

        if chunks and len(chunks) > 0:
            print(f"✅ Text chunking successful (created {len(chunks)} chunks)")
            for i, chunk in enumerate(chunks, 1):
                print(f"   Chunk {i}: {len(chunk)} characters")
            return True
        else:
            print("❌ Text chunking failed")
            return False

    except Exception as e:
        print(f"❌ Text chunking test failed: {e}")
        return False


def test_validators():
    """Test input validation functions"""
    print("\n✅ Testing input validators...")

    try:
        from utils.validators import validate_search_query

        # Test search query validation
        test_queries = [
            ("", False),  # Empty query
            ("ab", False),  # Too short
            ("Toyota", True),  # Valid query
            ("What is the fuel efficiency?", True),  # Valid query
        ]

        for query, expected in test_queries:
            is_valid, message = validate_search_query(query)
            if is_valid == expected:
                print(f"✅ Query validation for '{query}': {message}")
            else:
                print(
                    f"❌ Query validation failed for '{query}': expected {expected}, got {is_valid}"
                )
                return False

        return True

    except Exception as e:
        print(f"❌ Validator test failed: {e}")
        return False


def run_all_tests():
    """Run all tests"""
    print_header()

    tests = [
        ("Module Imports", test_imports),
        ("Configuration", test_configuration),
        ("Database Connection", test_database_connection),
        ("Google Authentication", test_google_authentication),
        ("Embedding Generation", test_embedding_generation),
        ("LLM Generation", test_llm_generation),
        ("Text Chunking", test_chunking),
        ("Input Validation", test_validators),
    ]

    results = []

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))

    # Print summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)

    passed = 0
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! Your system is ready to use.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the configuration and dependencies.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
