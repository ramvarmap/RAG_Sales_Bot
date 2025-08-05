# 🤖 Smart Chart RAG System

A complete **Retrieval Augmented Generation (RAG)** system with PDF processing, vector search, and AI-powered chat interface using a clean modular architecture.

## 🚀 Features

### 📄 PDF Processing
- **Drag & Drop Upload:** Easy PDF upload through Streamlit interface
- **Text Extraction:** Automatic text extraction from PDFs using PyPDF2
- **Hybrid Chunking:** Intelligent text chunking with semantic boundaries
- **Vector Embeddings:** Generate embeddings using Google Vertex AI
- **Database Storage:** Store embeddings in Oracle 23c AI vector database

### 💬 Interactive Chat
- **Natural Language Interface:** Ask questions about your documents
- **RAG-powered Responses:** AI answers based on retrieved content
- **Conversation History:** Maintains chat context across sessions
- **Source Citations:** References which documents were used
- **Comprehensive Search:** Uses all available information for complete answers

### 🎨 Beautiful UI
- **Streamlit Web Interface:** Professional, responsive design
- **Real-time Processing:** Live progress indicators
- **Error Handling:** Graceful error messages and user feedback
- **Session Management:** Persistent chat history
- **Document History:** Track all uploaded documents

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PDF Upload    │───▶│  Text Extract   │───▶│   Embeddings    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Chat Input    │◀───│   AI Response   │◀───│  Vector Search  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │                        │
                              ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │  Llama 3.3-70B  │    │ Oracle 23c AI   │
                       │   (Generation)  │    │ (Vector Store)  │
                       └─────────────────┘    └─────────────────┘
```

## 🛠️ Tech Stack

- **Frontend:** Streamlit
- **PDF Processing:** PyPDF2
- **Embeddings:** Google Vertex AI (text-embedding-005)
- **Vector Database:** Oracle 23c AI
- **AI Generation:** Llama 3.3-70B (Meta)
- **Authentication:** Google Service Account
- **Architecture:** Modular Python structure

## 📋 Prerequisites

- **Python 3.8+**
- **Oracle 23c AI Database** with vector support
- **Google Cloud Project** with Vertex AI enabled
- **Google Service Account** with appropriate permissions
- **Git** for version control

## 🚀 Complete Setup Guide

### Step 1: Clone the Repository
```bash
git clone <your-repo-url>
cd smart-chart
```

### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python -m venv smct-venv

# Activate virtual environment
# On Windows:
smct-venv\Scripts\activate
# On macOS/Linux:
source smct-venv/bin/activate
```

### Step 3: Install Dependencies
```bash
# Install all required packages
pip install -r requirements.txt
```

### Step 4: Set Up Google Cloud Credentials

1. **Create Google Cloud Project:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable Vertex AI API

2. **Create Service Account:**
   ```bash
   # Create service account key
   # Download JSON key file and save as secrets/llama-sa-key.json
   ```

3. **Required APIs:**
   - Vertex AI API
   - Cloud Storage API (if needed)

### Step 5: Set Up Oracle Database

1. **Oracle 23c AI Database:**
   - Ensure Oracle 23c AI is installed with vector support
   - Create a user with appropriate permissions
   - Note down connection details

2. **Database Schema:**
   ```sql
   -- The application will create required tables automatically
   -- Tables: DOCUMENTS, DOCUMENT_CHUNKS, CHUNKING_METADATA
   ```

### Step 6: Environment Configuration

Create a `.env` file in the root directory:

```env
# Google Cloud Configuration
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_APPLICATION_CREDENTIALS=secrets/llama-sa-key.json
ENDPOINT=us-central1-aiplatform.googleapis.com
REGION=us-central1
PROJECT_ID=your-project-id
VERTEX_PROJECT_ID=your-project-id
VERTEX_LOCATION=us-central1
VERTEX_EMBEDDING_MODEL=text-embedding-005

# Oracle Database Configuration
ORACLE_USERNAME=VECTOR_USER
ORACLE_PASSWORD=your-password
ORACLE_HOST=your-host
ORACLE_PORT=1521
ORACLE_SERVICE_NAME=your-service-name

# Application Configuration
BACKEND_URL=http://fastapi-backend:8000

# Chunking Configuration
TARGET_CHUNK_SIZE=1500
MAX_CHUNK_SIZE=2000
OVERLAP_SIZE=200
MIN_CHUNK_SIZE=500
DOCUMENT_SIZE_LIMIT=256000
```

### Step 7: Create Required Directories

```bash
# Create necessary directories
mkdir -p secrets
# No additional directories needed
mkdir -p testing
```

### Step 8: Place Service Account Key

```bash
# Copy your Google service account JSON key to:
secrets/llama-sa-key.json
```

### Step 9: Database Setup

```bash
# Run the automated setup script (recommended)
python setup.py

# Or manually create database tables
python -c "from database.operations import create_tables; create_tables()"
```

### Step 10: Test the Setup

```bash
# Test all connections and models
python testing/test_models.py
```

### Step 11: Run the Application

#### Option A: Streamlit Web Interface
```bash
streamlit run streamlit_app_modular.py
```
- Opens in browser at `http://localhost:8501`
- Two pages: PDF Upload and Chat Interface

#### Option B: Command-Line Interface
```bash
python cli_app_modular.py
```
- Interactive chat interface in terminal
- Type 'quit' to exit

## 📁 Project Structure

```
smart-chart/
├── README.md                    # Project documentation
├── requirements.txt             # Dependencies
├── .env                        # Environment variables (not in repo)
├── .gitignore                  # Git ignore rules
├── LICENSE                     # License file
│
├── streamlit_app_modular.py    # Main Streamlit application
├── cli_app_modular.py         # Command-line interface
│
├── config/                     # Configuration management
│   └── settings.py
│
├── database/                   # Database operations
│   ├── connection.py
│   └── operations.py
│
├── services/                   # External services
│   ├── auth.py
│   ├── embeddings.py
│   ├── llm.py
│   └── pdf.py
│
├── utils/                      # Utility functions
│   ├── chunking.py
│   └── validators.py
│
├── secrets/                    # Service account keys (not in repo)
│   └── llama-sa-key.json
│
# Removed analysis/ directory - not needed for stateless Cloud Run deployment
│   └── *.pdf
│
└── testing/                    # Test files
    ├── test_models.py
    └── reference/
```

## 📖 Usage

### Web Interface (Recommended)

1. **Start the Application:**
   ```bash
   streamlit run streamlit_app_modular.py
   ```

2. **Upload PDFs:**
   - Navigate to "📄 Upload PDFs" page
   - Drag & drop PDF files or click "Browse files"
   - Watch real-time processing progress
   - See confirmation when files are processed

3. **Chat with Documents:**
   - Navigate to "💬 Chat Interface" page
   - Type questions about your documents
   - Get AI-powered answers based on content
   - Ask follow-up questions for deeper conversations

### Command-Line Interface

```bash
python cli_app_modular.py
```

- Interactive chat interface in terminal
- Ask questions about your documents
- Type 'list' to see available documents
- Type 'quit' to exit

## 🎯 Example Questions

- "What are the available Toyota models?"
- "What is the fuel efficiency of the Toyota Corolla?"
- "Tell me about the engine specifications"
- "What safety features are available?"
- "Compare different models"
- "What is the warranty coverage?"

## 🔧 Configuration

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to service account key | `secrets/llama-sa-key.json` |
| `ORACLE_USERNAME` | Oracle database username | `VECTOR_USER` |
| `ORACLE_PASSWORD` | Oracle database password | `your-password` |
| `ORACLE_HOST` | Oracle database host | `your-host` |
| `ORACLE_PORT` | Oracle database port | `1521` |
| `ORACLE_SERVICE_NAME` | Oracle service name | `FREEPDB1` |
| `VERTEX_EMBEDDING_MODEL` | Vertex AI embedding model | `text-embedding-005` |

### Chunking Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `TARGET_CHUNK_SIZE` | Target chunk size in characters | `1500` |
| `MAX_CHUNK_SIZE` | Maximum chunk size | `2000` |
| `OVERLAP_SIZE` | Overlap between chunks | `200` |
| `MIN_CHUNK_SIZE` | Minimum chunk size | `500` |
| `DOCUMENT_SIZE_LIMIT` | Maximum PDF size in bytes | `256000` |

## 🧪 Testing

### Test All Components
```bash
python testing/test_models.py
```

This will test:
- ✅ Database connection
- ✅ Google Cloud authentication
- ✅ Vertex AI embedding model
- ✅ Llama 3.3-70B chat model

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Failed:**
   ```bash
   # Check .env file credentials
   # Ensure Oracle database is running
   # Verify network connectivity
   ```

2. **Google Cloud Authentication Failed:**
   ```bash
   # Verify service account key exists
   # Check file permissions
   # Ensure Vertex AI API is enabled
   ```

3. **PDF Upload Fails:**
   ```bash
   # Check file format (PDF only)
   # Ensure file is not corrupted
   # Verify file size limits
   ```

4. **AI Response Errors:**
   ```bash
   # Check Google Cloud credentials
   # Verify Vertex AI API access
   # Ensure sufficient quota
   ```

### Debug Commands

```bash
# Test database connection
python -c "from database.connection import test_connection; print(test_connection())"

# Test Google Cloud auth
python -c "from services.auth import generate_access_token; print(generate_access_token())"

# Test embedding generation
python -c "from services.embeddings import generate_embeddings_for_query; print(generate_embeddings_for_query('test', 'token'))"
```

## 🚀 Deployment

### Local Development
```bash
streamlit run streamlit_app_modular.py
```

### Production Deployment

1. **Environment Setup:**
   - Set production environment variables
   - Use production database credentials
   - Configure proper logging

2. **Security:**
   - Secure service account keys
   - Use environment variables for secrets
   - Enable HTTPS

3. **Monitoring:**
   - Set up application monitoring
   - Configure error tracking
   - Monitor API usage

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Vertex AI** for embedding and generation models
- **Oracle 23c AI** for vector database capabilities
- **Streamlit** for the beautiful web interface
- **Meta** for the Llama 3.3-70B model

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review console output for error messages
3. Open an issue on GitHub
4. Contact the development team

---

**Built with ❤️ for intelligent document processing and AI-powered conversations** # Deployment retry - Artifact Registry fixed - Mon Aug  4 20:04:56 IST 2025
