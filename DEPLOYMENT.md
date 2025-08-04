# 🚀 Smart Chart RAG - GCP Cloud Run Deployment Guide

This guide will help you deploy the Smart Chart RAG application to Google Cloud Platform using Cloud Run, Terraform, and GitHub Actions.

## 📋 Prerequisites

Before starting, ensure you have:

- ✅ **Google Cloud Project** with billing enabled
- ✅ **Google Cloud SDK** installed and configured
- ✅ **Oracle 23c AI Database** running on a remote server
- ✅ **Git** installed
- ✅ **GitHub account** with access to the repository
- ✅ **Terraform** (version >= 1.0) installed (optional, for local testing)

## 🏗️ Architecture Overview

```
GitHub Repository (testing branch)
    ↓
GitHub Actions Workflow
    ↓
Build Docker Image → Push to Artifact Registry
    ↓
Terraform Infrastructure → Deploy to Cloud Run
    ↓
Smart Chart RAG Application (Streamlit + Oracle DB + Vertex AI)
```

## 🚀 Quick Start Deployment

### Step 1: Clone the Repository

```bash
# Clone the repository
git clone <your-repository-url>
cd smart-chart

# Switch to the testing branch
git checkout testing
```

### Step 2: Set Up GCP Service Account

#### 2.1 Create Service Account

```bash
# Set your project ID (replace with your actual project ID)
export PROJECT_ID="your-gcp-project-id"

# Create service account
gcloud iam service-accounts create smart-chart-deploy \
    --display-name="Smart Chart Deployment Service Account"

# Get the service account email
SA_EMAIL="smart-chart-deploy@${PROJECT_ID}.iam.gserviceaccount.com"
```

#### 2.2 Grant Required Permissions

```bash
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
```

#### 2.3 Create and Download Service Account Key

```bash
# Create service account key
gcloud iam service-accounts keys create ~/smart-chart-sa-key.json \
    --iam-account=${SA_EMAIL}

# Verify the key was created
ls -la ~/smart-chart-sa-key.json
```

### Step 3: Create GCS Bucket for Terraform State

```bash
# Create bucket for Terraform state
gsutil mb -l us-central1 gs://smart-chart-terraform-state

# Verify bucket creation
gsutil ls gs://smart-chart-terraform-state
```

### Step 4: Enable Required GCP APIs

```bash
# Enable required APIs
gcloud services enable \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    aiplatform.googleapis.com \
    cloudbuild.googleapis.com
```

### Step 5: Set Up GitHub Secrets

#### 5.1 Navigate to GitHub Repository Settings

1. Go to your GitHub repository
2. Click **Settings** tab
3. Click **Secrets and variables** → **Actions**
4. Click **New repository secret**

#### 5.2 Add Required Secrets

Add these secrets one by one:

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
Copy the entire content of the `~/smart-chart-sa-key.json` file you created in Step 2.3.

### Step 6: Deploy the Application

#### 6.1 Push Code to Trigger Deployment

```bash
# Ensure you're on testing branch
git checkout testing

# Add all files
git add .

# Commit changes
git commit -m "Initial deployment setup"

# Push to trigger deployment
git push origin testing
```

#### 6.2 Monitor GitHub Actions Deployment

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

### Step 7: Verify Deployment

#### 7.1 Check Cloud Run Service

```bash
# List Cloud Run services
gcloud run services list --region=us-central1

# Get service details
gcloud run services describe smart-chart-rag --region=us-central1
```

#### 7.2 Access Your Application

1. Copy the Cloud Run URL from GitHub Actions output
2. Open the URL in your browser
3. You should see your Smart Chart RAG application

#### 7.3 Test Application Features

- ✅ Upload a PDF document
- ✅ Chat with the AI about the document
- ✅ Verify database connectivity

## 🔧 Local Testing (Optional)

If you want to test the Terraform configuration locally:

```bash
# Navigate to terraform directory
cd terraform

# Initialize Terraform
terraform init

# Test Terraform plan
terraform plan \
  -var="project_id=your-gcp-project-id" \
  -var="region=us-central1" \
  -var="container_image=us-central1-docker.pkg.dev/your-gcp-project-id/smart-chart-repo/smart-chart:latest" \
  -var="oracle_username=your-oracle-username" \
  -var="oracle_password=your-oracle-password" \
  -var="oracle_host=your-oracle-host-ip" \
  -var="oracle_port=1521" \
  -var="oracle_service_name=your-oracle-service-name"
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
gcloud projects get-iam-policy your-gcp-project-id \
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

- Check if all required files are present
- Verify Dockerfile syntax
- Ensure requirements.txt is up to date

#### Issue: GitHub Actions workflow fails

1. Check the Actions tab for detailed error logs
2. Verify all GitHub secrets are set correctly
3. Ensure GCP service account has proper permissions
4. Check if GCP APIs are enabled

### Check Logs

```bash
# View Cloud Run logs
gcloud run services logs read smart-chart-rag --region=us-central1

# View recent logs
gcloud run services logs read smart-chart-rag --region=us-central1 --limit=50
```

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
```

## 🎉 Success Indicators

Your deployment is successful when:

- ✅ GitHub Actions workflow completes without errors
- ✅ Cloud Run service shows "Ready" status
- ✅ Application URL is accessible
- ✅ You can upload PDFs and chat with the AI
- ✅ Database operations work correctly

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

1. Make changes to your code
2. Commit and push to the `testing` branch
3. GitHub Actions will automatically rebuild and deploy

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

## 🔒 Security Considerations

1. **Service Account**: The deployment uses a dedicated service account with minimal required permissions
2. **Secrets**: All sensitive data is stored as GitHub secrets
3. **Network**: Ensure your Oracle database is properly secured
4. **Access Control**: Consider setting up IAM policies for Cloud Run access

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review GitHub Actions logs for detailed error messages
3. Verify all prerequisites are met
4. Ensure GCP project has billing enabled
5. Check Oracle database connectivity

## 🏗️ Infrastructure Details

The deployment creates:

- **Artifact Registry Repository**: For storing Docker images
- **Service Account**: With necessary IAM permissions
- **Cloud Run Service**: Running your application
- **IAM Bindings**: Required permissions for the service account

## 📝 Notes

- The application runs on port 8080 (Cloud Run requirement)
- Oracle database must be accessible from Cloud Run's IP ranges
- All environment variables are set via Terraform
- The deployment is stateless (no persistent storage)

---

**Your Smart Chart RAG application is now deployed and running on GCP Cloud Run!** 🚀

For more information, check the [README.md](README.md) file in the repository. 