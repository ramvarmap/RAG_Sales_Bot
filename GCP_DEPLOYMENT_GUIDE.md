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

# Grant necessary roles
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/run.admin"

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/artifactregistry.admin"

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/iam.serviceAccountUser"

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member="serviceAccount:${SA_EMAIL}" \
    --role="roles/storage.admin"

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
```

### Step 5: Set Up GitHub Repository

#### 5.1 Create GitHub Repository

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

#### 5.2 Set Up GitHub Secrets

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

### Step 6: Configure Oracle Database

#### 6.1 Ensure Oracle Database is Accessible

Make sure your Oracle 23c AI database:
- Is running and accessible from the internet
- Has vector support enabled
- Has a user with appropriate permissions
- Is accessible from Cloud Run's IP ranges

#### 6.2 Test Database Connection

```bash
# Test database connectivity (replace with your actual values)
python -c "
from config.settings import DB_CONFIG
print('Database Config:', {k: v if k != 'password' else '***' for k, v in DB_CONFIG.items()})
"
```

### Step 7: Deploy Using GitHub Actions

#### 7.1 Trigger Deployment

```bash
# Push to testing branch to trigger deployment
git add .
git commit -m "Deploy to Cloud Run"
git push origin testing
```

#### 7.2 Monitor Deployment

1. Go to your GitHub repository
2. Click **Actions** tab
3. Click on the running workflow
4. Monitor the deployment progress

**Expected Workflow Steps:**
1. ✅ Checkout code
2. ✅ Set up Cloud SDK
3. ✅ Configure Docker
4. ✅ Build Docker image
5. ✅ Push to Artifact Registry
6. ✅ Setup Terraform
7. ✅ Terraform Init
8. ✅ Terraform Plan
9. ✅ Terraform Apply
10. ✅ Get Cloud Run URL

### Step 8: Verify Deployment

#### 8.1 Check Cloud Run Service

```bash
# List Cloud Run services
gcloud run services list --region=us-central1

# Get service details
gcloud run services describe smart-chart-rag --region=us-central1

# View service logs
gcloud run services logs read smart-chart-rag --region=us-central1 --limit=50
```

#### 8.2 Access Your Application

1. Copy the Cloud Run URL from GitHub Actions output
2. Open the URL in your browser
3. You should see your Smart Chart RAG application

#### 8.3 Test Application Features

- ✅ Upload a PDF document
- ✅ Chat with the AI about the document
- ✅ Verify database connectivity

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
```

## 📊 Monitoring and Maintenance

### Check Application Status

```bash
# Get Cloud Run service status
gcloud run services describe smart-chart-rag --region=us-central1

# Check service logs
gcloud run services logs read smart-chart-rag --region=us-central1
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

## 🎉 Success Indicators

Your deployment is successful when:

- ✅ GitHub Actions workflow completes without errors
- ✅ Cloud Run service shows "Ready" status
- ✅ Application URL is accessible
- ✅ You can upload PDFs and chat with the AI
- ✅ Database operations work correctly

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review GitHub Actions logs for detailed error messages
3. Verify all prerequisites are met
4. Ensure GCP project has billing enabled
5. Check Oracle database connectivity

---

**Your Smart Chart RAG application is now deployed and running on GCP Cloud Run!** 🚀

For more information, check the [README.md](README.md) and [DEPLOYMENT.md](DEPLOYMENT.md) files in the repository. 