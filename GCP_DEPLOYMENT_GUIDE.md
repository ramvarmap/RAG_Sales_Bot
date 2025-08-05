# 🚀 Complete GCP Cloud Run Deployment Guide

This guide provides step-by-step instructions to deploy the Smart Chart RAG application to Google Cloud Platform using Cloud Run.

## 📋 Prerequisites

Before starting, ensure you have:

- ✅ **Google Cloud Project** with billing enabled
- ✅ **Google Cloud SDK** installed and configured
- ✅ **Oracle 23c AI Database** running on a remote server
- ✅ **Git** installed
- ✅ **Docker** installed (for local testing)
- ✅ **Terraform** (version >= 1.0) installed

## 🏗️ Architecture Overview

```
GitHub Repository
    ↓
GitHub Actions Workflow
    ↓
Build Docker Image → Push to Artifact Registry
    ↓
Terraform Infrastructure → Deploy to Cloud Run
    ↓
Smart Chart RAG Application (Streamlit + Oracle DB + Vertex AI)
```

## 🔧 Key Authentication Changes

**Important**: The application has been updated to use **Application Default Credentials (ADC)** in Cloud Run environments, which is the recommended and secure approach for GCP applications.

### Authentication Strategy:
- **Cloud Run/GCP Environment**: Uses `google.auth.default()` (ADC)
- **Local Development**: Uses service account key file (`gcp_secrets/llama-sa-key.json`)
- **Automatic Detection**: The app detects the environment and chooses the appropriate authentication method

## 🚀 Step-by-Step Deployment

### Step 1: Clone and Prepare Repository

```bash
# Clone the repository
git clone <your-repository-url>
cd new_RAG

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Set Up Google Cloud Project

```bash
# Set your project ID
export PROJECT_ID="your-gcp-project-id"
gcloud config set project $PROJECT_ID

# Enable required APIs
gcloud services enable \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    aiplatform.googleapis.com \
    cloudbuild.googleapis.com \
    iam.googleapis.com

# Verify APIs are enabled
gcloud services list --enabled --filter="name:run.googleapis.com OR name:artifactregistry.googleapis.com OR name:aiplatform.googleapis.com"
```

### Step 3: Create Service Account

```bash
# Create service account for deployment
gcloud iam service-accounts create smart-chart-deploy \
    --display-name="Smart Chart Deployment Service Account"

# Get the service account email
SA_EMAIL="smart-chart-deploy@${PROJECT_ID}.iam.gserviceaccount.com"

# Grant minimal required roles (Least Privilege Principle)
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/run.developer"

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/artifactregistry.writer"

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/iam.serviceAccountUser"

# Add storage permissions for Terraform state
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/storage.objectAdmin"

# Create and download service account key
gcloud iam service-accounts keys create ~/smart-chart-sa-key.json \
    --iam-account=${SA_EMAIL}

# Verify the key was created
ls -la ~/smart-chart-sa-key.json
```

### Step 4: Create GCS Bucket for Terraform State

```bash
# Create bucket for Terraform state
gsutil mb -l us-central1 gs://smart-chart-terraform-state

# Verify bucket creation
gsutil ls gs://smart-chart-terraform-state

# Configure bucket IAM for Terraform state access
gsutil iam ch serviceAccount:${SA_EMAIL}:objectAdmin gs://smart-chart-terraform-state
```

### Step 5: Create Artifact Registry Repository

```bash
# Create Artifact Registry repository for Docker images
gcloud artifacts repositories create smart-chart-repo \
    --repository-format=docker \
    --location=us-central1 \
    --description="Docker repository for Smart Chart RAG application"

# Verify repository creation
gcloud artifacts repositories list --location=us-central1
```

### Step 6: Set Up GitHub Repository

#### 6.1 Create GitHub Repository

1. Go to GitHub and create a new repository
2. Push your code to the repository:

```bash
# Initialize git and push to GitHub
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/your-repo-name.git
git push -u origin main

# Create testing branch for deployment
git checkout -b testing
git push -u origin testing
```

#### 6.2 Set Up GitHub Secrets

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**

Add these secrets:

| Secret Name | Description | Example Value |
|-------------|-------------|---------------|
| `GCP_PROJECT_ID` | Your GCP Project ID | `my-project-123456` |
| `GCP_SA_KEY` | Service account JSON key | `{"type": "service_account", ...}` |
| `ORACLE_USERNAME` | Oracle database username | `VECTOR_USER` |
| `ORACLE_PASSWORD` | Oracle database password | `your-secure-password` |
| `ORACLE_HOST` | Oracle database host IP | `192.168.1.100` |
| `ORACLE_PORT` | Oracle database port | `1521` |
| `ORACLE_SERVICE_NAME` | Oracle database service name | `FREEPDB1` |

**For GCP_SA_KEY:**
Copy the entire content of the `~/smart-chart-sa-key.json` file.

### Step 7: Configure Oracle Database

#### 7.1 Ensure Oracle Database is Accessible

Make sure your Oracle 23c AI database:
- Is running and accessible from the internet
- Has vector support enabled
- Has a user with appropriate permissions
- Is accessible from Cloud Run's IP ranges

#### 7.2 Test Database Connection

```bash
# Test database connectivity (replace with your actual values)
python -c "
from config.settings import DB_CONFIG
print('Database Config:', {k: v if k != 'password' else '***' for k, v in DB_CONFIG.items()})
"
```

### Step 8: Deploy Using GitHub Actions

#### 8.1 Trigger Deployment

```bash
# Push to testing branch to trigger deployment
git add .
git commit -m "Deploy to Cloud Run"
git push origin testing
```

#### 8.2 Monitor Deployment

1. Go to your GitHub repository
2. Click **Actions** tab
3. Click on the running workflow
4. Monitor the deployment progress

**Expected Workflow Steps:**
1. ✅ Checkout code
2. ✅ Google Auth (using google-github-actions/auth@v2)
3. ✅ Set up Cloud SDK
4. ✅ Configure Docker
5. ✅ Build Docker image
6. ✅ Push to Artifact Registry
7. ✅ Setup Terraform
8. ✅ Terraform Init
9. ✅ Terraform Plan
10. ✅ Terraform Apply
11. ✅ Get Cloud Run URL
12. ✅ Make Cloud Run Service Public

### Step 12: Make Cloud Run Service Public

After successful deployment, make the service publicly accessible:

```bash
# Make Cloud Run service publicly invokable
gcloud run services add-iam-policy-binding smart-chart-rag \
    --region=us-central1 \
    --member="allUsers" \
    --role="roles/run.invoker"
```

### Step 13: Verify Deployment

#### 13.1 Check Cloud Run Service

```bash
# List Cloud Run services
gcloud run services list --region=us-central1

# Get service details
gcloud run services describe smart-chart-rag --region=us-central1

# View service logs
gcloud run services logs read smart-chart-rag --region=us-central1 --limit=50
```

#### 13.2 Access Your Application

1. Copy the Cloud Run URL from GitHub Actions output
2. Open the URL in your browser
3. You should see your Smart Chart RAG application

#### 13.3 Test Application Features

- ✅ Upload a PDF document
- ✅ Chat with the AI about the document
- ✅ Verify database connectivity
- ✅ Test embedding generation

## 🔧 Manual Deployment (Alternative)

If you prefer to deploy manually without GitHub Actions:

### Step 1: Build and Push Docker Image

```bash
# Set variables
export PROJECT_ID="your-gcp-project-id"
export REGION="us-central1"
export REPOSITORY="smart-chart-repo"

# Configure Docker for Artifact Registry
gcloud auth configure-docker ${REGION}-docker.pkg.dev

# Build Docker image
docker build -t ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/smart-chart:latest .

# Push Docker image
docker push ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/smart-chart:latest
```

### Step 2: Deploy with Terraform

```bash
# Navigate to terraform directory
cd terraform

# Initialize Terraform
terraform init

# Plan deployment
terraform plan \
  -var="project_id=${PROJECT_ID}" \
  -var="region=${REGION}" \
  -var="container_image=${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/smart-chart:latest" \
  -var="oracle_username=your-oracle-username" \
  -var="oracle_password=your-oracle-password" \
  -var="oracle_host=your-oracle-host-ip" \
  -var="oracle_port=1521" \
  -var="oracle_service_name=your-oracle-service-name"

# Apply deployment
terraform apply \
  -var="project_id=${PROJECT_ID}" \
  -var="region=${REGION}" \
  -var="container_image=${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/smart-chart:latest" \
  -var="oracle_username=your-oracle-username" \
  -var="oracle_password=your-oracle-password" \
  -var="oracle_host=your-oracle-host-ip" \
  -var="oracle_port=1521" \
  -var="oracle_service_name=your-oracle-service-name"

# Get the service URL
terraform output cloud_run_url
```

## 🐛 Troubleshooting

### Common Issues and Solutions

#### Issue: "Failed to generate embeddings!" Error

**Root Cause**: Application trying to read service account key file in Cloud Run
**Solution**: The authentication code has been updated to use ADC in Cloud Run environments

**Check**: Verify the `services/auth.py` file uses the updated authentication logic:

```python
# Check if we're running in Cloud Run or GCP environment
is_cloud_run = (
    os.getenv('K_SERVICE') or  # Cloud Run
    os.getenv('K_REVISION') or  # Cloud Run
    os.getenv('GOOGLE_CLOUD_PROJECT') or  # GCP environment
    os.getenv('GCP_PROJECT')  # Alternative GCP project env var
)

if is_cloud_run:
    # Use Application Default Credentials in Cloud Run/GCP
    credentials, project = default(scopes=scopes)
else:
    # Local development - use service account file
    credentials = service_account.Credentials.from_service_account_file(
        credentials_path, scopes=scopes)
```

#### Issue: "Permission denied for aiplatform.endpoints.predict"

**Root Cause**: Service account missing Vertex AI permissions
**Solution**: Add the `roles/aiplatform.user` role to the service account

```bash
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:smart-chart-deploy@${PROJECT_ID}.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"
```

#### Issue: "Forbidden Your client does not have permission to get URL"

**Root Cause**: Cloud Run service not publicly accessible
**Solution**: Make the service publicly invokable

```bash
gcloud run services add-iam-policy-binding smart-chart-rag \
    --region=us-central1 \
    --member="allUsers" \
    --role="roles/run.invoker"
```

#### Issue: Terraform state bucket not found

```bash
# Create bucket manually
gsutil mb -l us-central1 gs://smart-chart-terraform-state
```

#### Issue: Permission denied

```bash
# Verify service account permissions
gcloud projects get-iam-policy ${PROJECT_ID} \
    --flatten="bindings[].members" \
    --format="table(bindings.role)" \
    --filter="bindings.members:smart-chart-deploy"
```

#### Issue: Oracle connection failed

- Verify Oracle DB is accessible from Cloud Run
- Check firewall rules on your Oracle server
- Ensure Oracle service is running
- Verify network connectivity between GCP and your Oracle server

#### Issue: Docker build fails

```bash
# Check if all required files are present
ls -la

# Verify Dockerfile syntax
docker build --no-cache -t test-image .

# Check requirements.txt
pip install -r requirements.txt
```

#### Issue: GitHub Actions workflow fails

1. Check the Actions tab for detailed error logs
2. Verify all GitHub secrets are set correctly
3. Ensure GCP service account has proper permissions
4. Check if GCP APIs are enabled

### Debug Commands

```bash
# Check GCP project configuration
gcloud config get-value project

# List enabled APIs
gcloud services list --enabled

# Check service account
gcloud iam service-accounts list

# Verify Artifact Registry
gcloud artifacts repositories list --location=us-central1

# Check Cloud Run services
gcloud run services list --region=us-central1

# View recent logs
gcloud run services logs read smart-chart-rag --region=us-central1 --limit=50

# Check authentication in Cloud Run
gcloud run services logs read smart-chart-rag --region=us-central1 --filter="textPayload:\"Using Application Default Credentials\""
```

## 📊 Monitoring and Maintenance

### Check Application Status

```bash
# Get Cloud Run service status
gcloud run services describe smart-chart-rag --region=us-central1

# Check service logs
gcloud run services logs read smart-chart-rag --region=us-central1

# Check authentication logs
gcloud run services logs read smart-chart-rag --region=us-central1 --filter="textPayload:\"Access token generated successfully\""
```

### Update Application

To update your application:

```bash
# Make your changes
git add .
git commit -m "Update application"
git push origin testing
```

### Scale Application

```bash
# Update Cloud Run service with more resources
gcloud run services update smart-chart-rag \
    --region=us-central1 \
    --cpu=4 \
    --memory=8Gi \
    --max-instances=10
```

### Clean Up Resources

```bash
# Destroy Terraform resources
cd terraform
terraform destroy

# Delete service account
gcloud iam service-accounts delete smart-chart-deploy@${PROJECT_ID}.iam.gserviceaccount.com

# Delete Artifact Registry repository
gcloud artifacts repositories delete smart-chart-repo --location=us-central1

# Delete GCS bucket
gsutil rm -r gs://smart-chart-terraform-state
```

## 🔒 Security Considerations

1. **Service Account**: Uses dedicated service account with minimal required permissions
2. **Secrets**: All sensitive data stored as GitHub secrets
3. **Network**: Ensure Oracle database is properly secured
4. **Access Control**: Consider setting up IAM policies for Cloud Run access
5. **HTTPS**: Cloud Run automatically provides HTTPS endpoints
6. **Authentication**: Uses Application Default Credentials (ADC) in Cloud Run - no service account keys in containers
7. **Terraform State**: Stored securely in GCS with modern IAM permissions and state locking

## 📦 Terraform State Security

### **State Storage Configuration:**
- **Location**: `gs://smart-chart-terraform-state/terraform/state/`
- **State File**: `default.tfstate`
- **Locking**: Automatic state locking prevents concurrent modifications
- **Versioning**: GCS provides automatic versioning and backup

### **Access Control:**
- **Service Account**: `smart-chart-deploy` has `roles/storage.objectAdmin` on the state bucket
- **Modern IAM**: Uses modern IAM permissions instead of legacy bucket permissions
- **Least Privilege**: Only the deployment service account can access state files
- **Audit Logging**: All state access is logged for security monitoring

## 📝 Environment Variables

The application uses these environment variables (set via Terraform):

| Variable | Description | Default |
|----------|-------------|---------|
| `ORACLE_USERNAME` | Oracle database username | - |
| `ORACLE_PASSWORD` | Oracle database password | - |
| `ORACLE_HOST` | Oracle database host | - |
| `ORACLE_PORT` | Oracle database port | 1521 |
| `ORACLE_SERVICE_NAME` | Oracle database service name | - |
| `VERTEX_PROJECT_ID` | GCP Project ID | - |
| `VERTEX_LOCATION` | Vertex AI location | us-central1 |
| `VERTEX_EMBEDDING_MODEL` | Embedding model | text-embedding-005 |
| `TARGET_CHUNK_SIZE` | Target chunk size | 1500 |
| `MAX_CHUNK_SIZE` | Maximum chunk size | 2000 |
| `OVERLAP_SIZE` | Overlap between chunks | 200 |
| `MIN_CHUNK_SIZE` | Minimum chunk size | 500 |
| `DOCUMENT_SIZE_LIMIT` | Maximum PDF size | 256000 |

## 🔧 Authentication Architecture

### Cloud Run Environment
- **Method**: Application Default Credentials (ADC)
- **Service Account**: `smart-chart-deploy@project-id.iam.gserviceaccount.com`
- **Required Roles**: 
  - `roles/aiplatform.user` - Vertex AI access for embeddings and LLM
  - `roles/run.developer` - Deploy and manage Cloud Run services
  - `roles/artifactregistry.writer` - Push Docker images to Artifact Registry
  - `roles/iam.serviceAccountUser` - Run operations as service account
  - `roles/storage.objectAdmin` - Manage Terraform state files in GCS (includes read/write/delete)
- **Bucket IAM**: Service account also has `objectAdmin` role on the Terraform state bucket
- **Security**: Least privilege principle - minimal required permissions only
- **Removed Roles**: 
  - ❌ `roles/run.admin` - Was overly broad (full Cloud Run control)
  - ❌ `roles/artifactregistry.admin` - Was overly broad (full Artifact Registry control)
  - ❌ `roles/storage.admin` - Was overly broad (full GCS control)

### Local Development
- **Method**: Service account key file
- **Location**: `gcp_secrets/llama-sa-key.json`
- **Fallback**: ADC if key file not found

### Environment Detection
The application automatically detects the environment using these variables:
- `K_SERVICE` (Cloud Run)
- `K_REVISION` (Cloud Run)
- `GOOGLE_CLOUD_PROJECT` (GCP environment)
- `GCP_PROJECT` (Alternative GCP project env var)

## 🎉 Success Indicators

Your deployment is successful when:

- ✅ GitHub Actions workflow completes without errors
- ✅ Cloud Run service shows "Ready" status
- ✅ Cloud Run service is publicly accessible
- ✅ Application URL is accessible
- ✅ You can upload PDFs and chat with the AI
- ✅ Database operations work correctly
- ✅ Embedding generation works without errors
- ✅ Authentication logs show "Using Application Default Credentials for Cloud Run"
- ✅ Terraform state is securely stored and accessible

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review GitHub Actions logs for detailed error messages
3. Verify all prerequisites are met
4. Ensure GCP project has billing enabled
5. Check Oracle database connectivity
6. Verify service account has `roles/aiplatform.user` role
7. Check authentication logs for ADC usage

---

**Your Smart Chart RAG application is now deployed and running on GCP Cloud Run!** 🚀

For more information, check the [README.md](README.md) and [DEPLOYMENT.md](DEPLOYMENT.md) files in the repository. 