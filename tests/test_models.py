#!/usr/bin/env python3
"""
Test suite for Smart Chart RAG System
Comprehensive testing for all application components
"""

import pytest
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Import application modules
from config.settings import DB_CONFIG, GOOGLE_CONFIG, CHUNKING_CONFIG
from services.auth import generate_access_token
from services.pdf import extract_text_from_pdf, validate_document_requirements
from services.embeddings import generate_embeddings_for_query
from services.llm import generate_llama_response
from utils.validators import validate_pdf_file, validate_search_query
from utils.chunking import create_chunks


class TestConfiguration:
    """Test configuration settings"""
    
    def test_db_config_structure(self):
        """Test database configuration structure"""
        assert 'username' in DB_CONFIG
        assert 'password' in DB_CONFIG
        assert 'host' in DB_CONFIG
        assert 'port' in DB_CONFIG
        assert 'service_name' in DB_CONFIG
    
    def test_google_config_structure(self):
        """Test Google Cloud configuration structure"""
        assert 'project_id' in GOOGLE_CONFIG
        assert 'location' in GOOGLE_CONFIG
        assert 'embedding_model' in GOOGLE_CONFIG
        assert 'llm_model' in GOOGLE_CONFIG
    
    def test_chunking_config_structure(self):
        """Test chunking configuration structure"""
        assert 'target_size' in CHUNKING_CONFIG
        assert 'max_size' in CHUNKING_CONFIG
        assert 'overlap' in CHUNKING_CONFIG
        assert 'min_size' in CHUNKING_CONFIG
        assert 'document_size_limit' in CHUNKING_CONFIG


class TestAuthentication:
    """Test authentication services"""
    
    @patch('services.auth.default')
    @patch('os.getenv')
    def test_generate_access_token_cloud_run(self, mock_getenv, mock_default):
        """Test access token generation in Cloud Run environment"""
        # Mock Cloud Run environment
        mock_getenv.side_effect = lambda x: {
            'K_SERVICE': 'smart-chart-rag',
            'VERTEX_PROJECT_ID': 'test-project'
        }.get(x)
        
        # Mock credentials
        mock_credentials = Mock()
        mock_credentials.token = "test-token"
        mock_default.return_value = (mock_credentials, "test-project")
        
        # Test
        token = generate_access_token()
        
        assert token == "test-token"
        mock_default.assert_called_once()
    
    @patch('services.auth.service_account.Credentials.from_service_account_file')
    @patch('os.path.exists')
    @patch('os.getenv')
    def test_generate_access_token_local(self, mock_getenv, mock_exists, mock_sa_creds):
        """Test access token generation in local environment"""
        # Mock local environment
        mock_getenv.return_value = None
        mock_exists.return_value = True
        
        # Mock credentials
        mock_credentials = Mock()
        mock_credentials.token = "test-token"
        mock_sa_creds.return_value = mock_credentials
        
        # Test
        token = generate_access_token()
        
        assert token == "test-token"
        mock_sa_creds.assert_called_once()


class TestPDFProcessing:
    """Test PDF processing services"""
    
    def test_validate_document_requirements_valid(self):
        """Test document requirements validation with valid file"""
        # Create a mock PDF file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            f.write(b'%PDF-1.4\n%Test PDF content')
            temp_pdf = f.name
        
        try:
            result = validate_document_requirements(temp_pdf)
            assert result is True
        finally:
            os.unlink(temp_pdf)
    
    def test_validate_document_requirements_invalid_extension(self):
        """Test document requirements validation with invalid extension"""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            f.write(b'Test content')
            temp_file = f.name
        
        try:
            result = validate_document_requirements(temp_file)
            assert result is False
        finally:
            os.unlink(temp_file)
    
    def test_validate_document_requirements_file_too_large(self):
        """Test document requirements validation with file too large"""
        # Create a large file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            f.write(b'%PDF-1.4\n' + b'x' * (CHUNKING_CONFIG['document_size_limit'] + 1000))
            temp_pdf = f.name
        
        try:
            result = validate_document_requirements(temp_pdf)
            assert result is False
        finally:
            os.unlink(temp_pdf)


class TestValidators:
    """Test validation utilities"""
    
    def test_validate_pdf_file_valid(self):
        """Test PDF file validation with valid file"""
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            f.write(b'%PDF-1.4\n%Test PDF content')
            temp_pdf = f.name
        
        try:
            result = validate_pdf_file(temp_pdf)
            assert result is True
        finally:
            os.unlink(temp_pdf)
    
    def test_validate_pdf_file_invalid(self):
        """Test PDF file validation with invalid file"""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            f.write(b'Not a PDF file')
            temp_file = f.name
        
        try:
            result = validate_pdf_file(temp_file)
            assert result is False
        finally:
            os.unlink(temp_file)
    
    def test_validate_search_query_valid(self):
        """Test search query validation with valid query"""
        valid_queries = [
            "What is Toyota?",
            "Tell me about the features",
            "How does the engine work?",
            "A" * 100  # Long query
        ]
        
        for query in valid_queries:
            result = validate_search_query(query)
            assert result is True
    
    def test_validate_search_query_invalid(self):
        """Test search query validation with invalid query"""
        invalid_queries = [
            "",  # Empty query
            "   ",  # Whitespace only
            "A" * 1001,  # Too long
        ]
        
        for query in invalid_queries:
            result = validate_search_query(query)
            assert result is False


class TestChunking:
    """Test text chunking utilities"""
    
    def test_create_chunks_basic(self):
        """Test basic chunk creation"""
        text = "This is a test document. " * 50  # Create long text
        chunks = create_chunks(text, target_size=100, overlap=20)
        
        assert len(chunks) > 0
        assert all(len(chunk) <= 100 for chunk in chunks)
    
    def test_create_chunks_with_overlap(self):
        """Test chunk creation with overlap"""
        text = "Sentence one. Sentence two. Sentence three. " * 10
        chunks = create_chunks(text, target_size=50, overlap=10)
        
        assert len(chunks) > 1
        # Check that consecutive chunks have some overlap
        for i in range(len(chunks) - 1):
            overlap_found = False
            for j in range(min(10, len(chunks[i]))):
                if chunks[i][-j:] in chunks[i + 1]:
                    overlap_found = True
                    break
            assert overlap_found
    
    def test_create_chunks_short_text(self):
        """Test chunk creation with short text"""
        text = "Short text that doesn't need chunking."
        chunks = create_chunks(text, target_size=100, overlap=20)
        
        assert len(chunks) == 1
        assert chunks[0] == text


class TestEmbeddings:
    """Test embedding generation"""
    
    @patch('services.embeddings.requests.post')
    def test_generate_embeddings_for_query_success(self, mock_post):
        """Test successful embedding generation"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'predictions': [{
                'embeddings': {
                    'values': [0.1, 0.2, 0.3] * 100  # 768-dimensional vector
                }
            }]
        }
        mock_post.return_value = mock_response
        
        # Test
        embeddings = generate_embeddings_for_query("test query", "test-token")
        
        assert embeddings is not None
        assert len(embeddings) == 768
        assert all(isinstance(x, float) for x in embeddings)
    
    @patch('services.embeddings.requests.post')
    def test_generate_embeddings_for_query_failure(self, mock_post):
        """Test embedding generation failure"""
        # Mock failed response
        mock_response = Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response
        
        # Test
        embeddings = generate_embeddings_for_query("test query", "test-token")
        
        assert embeddings is None


class TestLLM:
    """Test LLM response generation"""
    
    @patch('services.llm.requests.post')
    def test_generate_llama_response_success(self, mock_post):
        """Test successful LLM response generation"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [{
                'message': {
                    'content': 'This is a test response from the LLM.'
                }
            }]
        }
        mock_post.return_value = mock_response
        
        # Test
        response = generate_llama_response("test query", "test context", "test-token")
        
        assert response is not None
        assert "test response" in response.lower()
    
    @patch('services.llm.requests.post')
    def test_generate_llama_response_failure(self, mock_post):
        """Test LLM response generation failure"""
        # Mock failed response
        mock_response = Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response
        
        # Test
        response = generate_llama_response("test query", "test context", "test-token")
        
        assert response is None


class TestIntegration:
    """Integration tests"""
    
    def test_configuration_integration(self):
        """Test that all configurations work together"""
        # Test that required environment variables are handled
        assert isinstance(CHUNKING_CONFIG['target_size'], int)
        assert isinstance(CHUNKING_CONFIG['max_size'], int)
        assert isinstance(CHUNKING_CONFIG['overlap'], int)
        assert CHUNKING_CONFIG['target_size'] <= CHUNKING_CONFIG['max_size']
        assert CHUNKING_CONFIG['overlap'] < CHUNKING_CONFIG['target_size']
    
    def test_validation_integration(self):
        """Test validation functions work together"""
        # Test that validation functions handle edge cases
        assert validate_search_query("") is False
        assert validate_search_query("valid query") is True
        
        # Test file validation
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            f.write(b'%PDF-1.4\n%Test')
            temp_pdf = f.name
        
        try:
            assert validate_pdf_file(temp_pdf) is True
        finally:
            os.unlink(temp_pdf)


# Test fixtures
@pytest.fixture
def sample_pdf_file():
    """Create a sample PDF file for testing"""
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
        f.write(b'%PDF-1.4\n%Test PDF content for testing')
        yield f.name
        os.unlink(f.name)


@pytest.fixture
def sample_text():
    """Sample text for chunking tests"""
    return "This is a sample text for testing chunking functionality. " * 20


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 