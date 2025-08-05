# 🚀 Smart Chart RAG - Complete GCP Deployment Guide

This guide provides step-by-step instructions to deploy the Smart Chart RAG application to Google Cloud Platform using Cloud Run with automated infrastructure management.

## 📋 Prerequisites

Before starting, ensure you have:

- ✅ **Google Cloud Project** with billing enabled
- ✅ **Google Cloud SDK** installed and configured
- ✅ **Oracle 23c AI Database** running on a remote server
- ✅ **Git** installed
- ✅ **Terraform** (version >= 1.0) installed

## 🏗️ Architecture Overview

```
GitHub Repository
    ↓
Bootstrap Script (One-time setup)
    ↓
GitHub Actions Workflow (Automated deployment)
    ↓
Build Docker Image → Push to Artifact Registry
    ↓
Terraform Infrastructure → Deploy to Cloud Run
    ↓
Smart Chart RAG Application (Streamlit + Oracle DB + Vertex AI)
```

## 🔧 Infrastructure Management Strategy

### **Bootstrap Script** (`bootstrap.sh`)
Handles all foundational infrastructure:
- ✅ **Google Cloud APIs** - Enables required services
- ✅ **GCS Bucket** - Terraform state storage
- ✅ **Service Account** - With all necessary IAM roles
- ✅ **Artifact Registry** - Docker repository
- ✅ **Service Account Key** - For GitHub Actions

### **Terraform** (`terraform/`)
Manages application-specific infrastructure:
- ✅ **Cloud Run Service** - Application deployment
- ✅ **Public Access** - IAM policy for public access
- ✅ **Data Sources** - References existing bootstrap resources

### **GitHub Actions** (`.github/workflows/deploy.yml`)
Automated CI/CD pipeline:
- ✅ **Docker Build & Push** - Container image management
- ✅ **Terraform Apply** - Infrastructure deployment
- ✅ **Environment Variables** - Dynamic configuration

## 🚀 Step-by-Step Deployment

### **Step 1: Clone and Prepare Repository**

```bash
# Clone the repository
git clone https://github.com/ramvarmap/RAG_Sales_Bot.git
cd RAG_Sales_Bot

# Switch to testing branch
git checkout testing

# Make bootstrap script executable
chmod +x bootstrap.sh
```

### **Step 2: Configure Google Cloud**

```bash
# Set your project ID
export PROJECT_ID="your-gcp-project-id"
gcloud config set project $PROJECT_ID

# Set region (optional, defaults to us-central1)
gcloud config set compute/region us-central1

# Verify configuration
gcloud config list
```

### **Step 3: Run Bootstrap Script (One-time Setup)**

```bash
# Run the bootstrap script
./bootstrap.sh
```

**What the bootstrap script does:**
- ✅ Enables required Google Cloud APIs
- ✅ Creates GCS bucket for Terraform state
- ✅ Creates service account with all necessary roles
- ✅ Creates Artifact Registry repository
- ✅ Generates service account key file

**Expected output:**
```
🎉 Bootstrap completed successfully!

📦 Created resources:
   • GCS Bucket: gs://smart-chart-terraform-state
   • Service Account: smart-chart-deploy@your-project.iam.gserviceaccount.com
   • Artifact Registry: smart-chart-repo
   • Service Account Key: smart-chart-deploy-key.json

🔧 Enabled APIs:
   • storage.googleapis.com
   • iam.googleapis.com
   • artifactregistry.googleapis.com
   • run.googleapis.com
   • aiplatform.googleapis.com

🔑 Assigned IAM Roles:
   • roles/storage.objectAdmin (Terraform state management)
   • roles/iam.serviceAccountUser (Cloud Run service account usage)
   • roles/artifactregistry.writer (Docker image uploads)
   • roles/aiplatform.user (Vertex AI model access)
   • roles/run.developer (Cloud Run deployment)
   • roles/run.invoker (Cloud Run service invocation)
```

### **Step 4: Configure GitHub Repository Secrets**

Go to your GitHub repository → Settings → Secrets and variables → Actions

**Required Secrets:**
```
GCP_PROJECT_ID = your-gcp-project-id
GCP_SA_KEY = [Content of smart-chart-deploy-key.json file]
ORACLE_USERNAME = VECTOR_USER
ORACLE_PASSWORD = Oracle123
ORACLE_HOST = inflabs.itversity.com
ORACLE_PORT = 1521
ORACLE_SERVICE_NAME = FREEPDB1
```

**How to add GCP_SA_KEY:**
1. Copy the content of `smart-chart-deploy-key.json` file
2. Create new repository secret named `GCP_SA_KEY`
3. Paste the entire JSON content as the value

### **Step 5: Deploy Application**

**Option A: Automatic Deployment (Recommended)**
```bash
# Push to testing branch to trigger deployment
git add .
git commit -m "Initial deployment"
git push origin testing
```

**Option B: Manual Deployment**
1. Go to GitHub repository → Actions tab
2. Select "Build and Deploy to Cloud Run" workflow
3. Click "Run workflow"
4. Select "testing" branch
5. Click "Run workflow"

### **Step 6: Monitor Deployment**

**GitHub Actions Workflow Steps:**
1. ✅ **Checkout code** - Downloads repository
2. ✅ **Google Auth** - Authenticates with GCP
3. ✅ **Build Docker image** - Creates container image
4. ✅ **Push to Artifact Registry** - Stores image
5. ✅ **Terraform Init** - Initializes Terraform
6. ✅ **Terraform Plan** - Shows infrastructure changes
7. ✅ **Terraform Apply** - Deploys infrastructure
8. ✅ **Get Cloud Run URL** - Retrieves service URL

**Expected Terraform Plan Output:**
```
Plan: 0 to add, 1 to change, 0 to destroy.

# google_cloud_run_service.smart_chart will be updated in-place
~ resource "google_cloud_run_service" "smart_chart" {
    ~ template {
        ~ spec {
            ~ containers {
                ~ image = "old-image" -> "new-image"
            }
        }
    }
}
```

## 🔍 Troubleshooting

### **Common Issues and Solutions**

#### **1. Bootstrap Script Errors**

**Error:** `Permission denied`
```bash
# Solution: Make script executable
chmod +x bootstrap.sh
```

**Error:** `Service account already exists`
```bash
# Solution: This is normal, script will skip creation
```

**Error:** `API already enabled`
```bash
# Solution: This is normal, script will skip enabling
```

#### **2. GitHub Actions Errors**

**Error:** `Authentication failed`
```bash
# Solution: Verify GCP_SA_KEY secret is correctly set
# Check that the JSON content is complete and valid
```

**Error:** `Docker push failed`
```bash
# Solution: Verify Artifact Registry exists
# Run bootstrap script again if needed
```

**Error:** `Terraform plan failed`
```bash
# Solution: Check terraform.tfvars file generation
# Verify all required secrets are set
```

#### **3. Application Errors**

**Error:** `Failed to establish connections`
```bash
# Solution: Check Oracle database connectivity
# Verify environment variables are set correctly
# Check Cloud Run logs for detailed error messages
```

**Error:** `Authentication failed for Vertex AI`
```bash
# Solution: Verify service account has aiplatform.user role
# Check that APIs are enabled
```

### **Debugging Commands**

**Check Cloud Run Logs:**
```bash
gcloud run services logs read smart-chart-rag --region=us-central1 --limit=50
```

**Check Terraform State:**
```bash
cd terraform
terraform state list
terraform plan
```

**Test Database Connection:**
```bash
# Check if Oracle database is accessible
telnet inflabs.itversity.com 1521
```

**Verify Service Account Permissions:**
```bash
gcloud projects get-iam-policy your-project-id \
  --flatten="bindings[].members" \
  --filter="bindings.members:smart-chart-deploy@your-project.iam.gserviceaccount.com" \
  --format="table(bindings.role)"
```

## 🔧 Configuration Management

### **Environment Variables**

**Oracle Database:**
- `ORACLE_USERNAME` - Database username
- `ORACLE_PASSWORD` - Database password
- `ORACLE_HOST` - Database host
- `ORACLE_PORT` - Database port
- `ORACLE_SERVICE_NAME` - Database service name

**Google Cloud:**
- `VERTEX_PROJECT_ID` - GCP project ID
- `VERTEX_LOCATION` - GCP region
- `VERTEX_EMBEDDING_MODEL` - Embedding model name

### **Application Settings**

**Chunking Configuration:**
- Target chunk size: 1500 characters
- Maximum chunk size: 2000 characters
- Overlap size: 200 characters
- Document size limit: 250 KB

**Search Configuration:**
- Top K results: 8
- Similarity threshold: 0.7

## 🔄 Update and Maintenance

### **Code Updates**
```bash
# Make your changes
git add .
git commit -m "Update description"
git push origin testing
# GitHub Actions will automatically deploy
```

### **Infrastructure Updates**
```bash
# Modify terraform/main.tf
git add .
git commit -m "Update infrastructure"
git push origin testing
```

### **Configuration Updates**
```bash
# Update GitHub secrets
# Push to trigger redeployment
git commit --allow-empty -m "Update configuration"
git push origin testing
```

## 📊 Monitoring and Logs

### **Cloud Run Monitoring**
- **URL:** `https://smart-chart-rag-xxxxx-uc.a.run.app`
- **Logs:** Google Cloud Console → Cloud Run → smart-chart-rag → Logs
- **Metrics:** Google Cloud Console → Cloud Run → smart-chart-rag → Metrics

### **GitHub Actions Monitoring**
- **URL:** GitHub repository → Actions tab
- **Workflow:** "Build and Deploy to Cloud Run"
- **Status:** Real-time deployment status

### **Terraform State**
- **Backend:** GCS bucket `smart-chart-terraform-state`
- **Location:** `gs://smart-chart-terraform-state/terraform/state`
- **Management:** Terraform manages state automatically

## 🎯 Success Indicators

### **Deployment Success:**
- ✅ GitHub Actions workflow completes successfully
- ✅ Cloud Run service is accessible
- ✅ Application loads without errors
- ✅ Database connection established
- ✅ Vertex AI authentication works

### **Application Success:**
- ✅ PDF upload functionality works
- ✅ Text extraction and chunking works
- ✅ Embedding generation works
- ✅ Chat interface responds correctly
- ✅ Search functionality works

## 🔒 Security Best Practices

### **Implemented Security Measures:**
- ✅ **Least Privilege Principle** - Service account has minimal required roles
- ✅ **Application Default Credentials** - Secure authentication in Cloud Run
- ✅ **Environment Variables** - Sensitive data not hardcoded
- ✅ **Terraform State Security** - State stored in GCS with versioning
- ✅ **Public Access Control** - Only Cloud Run service is publicly accessible

### **Security Recommendations:**
- 🔒 **Regular Key Rotation** - Rotate service account keys periodically
- 🔒 **Access Monitoring** - Monitor service account usage
- 🔒 **Secret Management** - Consider using Secret Manager for sensitive data
- 🔒 **Network Security** - Consider VPC for additional network isolation

## 📚 Additional Resources

- **Google Cloud Documentation:** https://cloud.google.com/docs
- **Terraform Documentation:** https://www.terraform.io/docs
- **GitHub Actions Documentation:** https://docs.github.com/en/actions
- **Streamlit Documentation:** https://docs.streamlit.io
- **Oracle Database Documentation:** https://docs.oracle.com/en/database/

---

**🎉 Congratulations! Your Smart Chart RAG application is now deployed and ready to use!** 