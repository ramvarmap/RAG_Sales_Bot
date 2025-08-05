# 🚀 Smart Chart RAG - Terraform Infrastructure

This directory contains the Terraform configuration for deploying the Smart Chart RAG application on Google Cloud Platform.

## 📋 Overview

The Terraform configuration manages all infrastructure components except the backend GCS bucket (which is created by the bootstrap script):

- **Google Cloud APIs** - Enables required services
- **Service Account** - Creates and configures the deployment service account
- **IAM Roles** - Assigns all necessary permissions
- **Artifact Registry** - Creates Docker repository for images
- **Cloud Run Service** - Deploys the application with proper configuration
- **Public Access** - Makes the service publicly accessible

## 🏗️ Infrastructure Components

### 1. Google Cloud APIs
```hcl
resource "google_project_service" "required_apis" {
  for_each = toset([
    "storage.googleapis.com",           # For GCS bucket
    "iam.googleapis.com",              # For service accounts
    "artifactregistry.googleapis.com", # For Docker registry
    "run.googleapis.com",              # For Cloud Run
    "aiplatform.googleapis.com"        # For Vertex AI
  ])
}
```

### 2. Service Account
```hcl
resource "google_service_account" "cloud_run_sa" {
  account_id   = "smart-chart-deploy"
  display_name = "Smart Chart RAG Deployment Service Account"
  description  = "Service account for Smart Chart RAG application deployment"
}
```

### 3. IAM Roles
The service account is assigned the following roles:
- `roles/storage.objectAdmin` - Terraform state management
- `roles/iam.serviceAccountUser` - Cloud Run service account usage
- `roles/artifactregistry.writer` - Docker image uploads
- `roles/aiplatform.user` - Vertex AI model access
- `roles/run.developer` - Cloud Run deployment
- `roles/run.invoker` - Cloud Run service invocation

### 4. Artifact Registry
```hcl
resource "google_artifact_registry_repository" "smart_chart" {
  location      = var.region
  repository_id = "smart-chart-repo"
  description   = "Docker repository for Smart Chart RAG application"
  format        = "DOCKER"
}
```

### 5. Cloud Run Service
```hcl
resource "google_cloud_run_service" "smart_chart" {
  name     = "smart-chart-rag"
  location = var.region
  
  template {
    spec {
      service_account_name = google_service_account.cloud_run_sa.email
      containers {
        image = var.container_image
        # Environment variables for Oracle DB and Vertex AI
      }
    }
  }
}
```

## 🚀 Quick Start

### Prerequisites
1. **Google Cloud CLI** installed and authenticated
2. **Terraform** installed (version >= 1.0)
3. **GCP Project** with billing enabled

### Step 1: Bootstrap (One-time setup)
```bash
# Run the bootstrap script to create the Terraform state bucket
chmod +x ../bootstrap.sh
./../bootstrap.sh
```

### Step 2: Configure Variables
```bash
# Copy the example variables file
cp terraform.tfvars.example terraform.tfvars

# Edit terraform.tfvars with your values
nano terraform.tfvars
```

### Step 3: Initialize Terraform
```bash
# Initialize Terraform with the GCS backend
terraform init
```

### Step 4: Plan and Apply
```bash
# Review the planned changes
terraform plan

# Apply the configuration
terraform apply
```

## 📝 Configuration

### Required Variables

Create a `terraform.tfvars` file with the following variables:

```hcl
# GCP Project Configuration
project_id = "your-gcp-project-id"
region     = "us-central1"

# Docker Image Configuration
container_image = "us-central1-docker.pkg.dev/your-gcp-project-id/smart-chart-repo/smart-chart:latest"

# Oracle Database Configuration
oracle_username     = "VECTOR_USER"
oracle_password     = "Oracle123"
oracle_host         = "inflabs.itversity.com"
oracle_port         = "1521"
oracle_service_name = "FREEPDB1"
```

### Variable Descriptions

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `project_id` | GCP Project ID | Yes | - |
| `region` | GCP region for resources | No | `us-central1` |
| `container_image` | Docker image URL for Cloud Run | Yes | - |
| `oracle_username` | Oracle database username | Yes | - |
| `oracle_password` | Oracle database password | Yes | - |
| `oracle_host` | Oracle database host | Yes | - |
| `oracle_port` | Oracle database port | No | `1521` |
| `oracle_service_name` | Oracle database service name | Yes | - |

## 🔧 Management Commands

### View Current State
```bash
terraform show
```

### View Outputs
```bash
terraform output
```

### Update Infrastructure
```bash
terraform plan
terraform apply
```

### Destroy Infrastructure
```bash
terraform destroy
```

## 📊 Outputs

After successful deployment, Terraform provides the following outputs:

- `cloud_run_service_url` - URL of the deployed Cloud Run service
- `service_account_email` - Email of the service account used by Cloud Run
- `artifact_registry_location` - Location of the Artifact Registry repository
- `artifact_registry_name` - Name of the Artifact Registry repository
- `project_id` - Project ID where resources are deployed
- `region` - Region where resources are deployed

## 🔒 Security

### Service Account Permissions
The service account follows the principle of least privilege with only the necessary permissions:

- **Terraform Operations**: `storage.objectAdmin`, `iam.serviceAccountUser`
- **Application Runtime**: `aiplatform.user`, `run.developer`, `run.invoker`
- **Deployment**: `artifactregistry.writer`

### Public Access
The Cloud Run service is made publicly accessible via:
```hcl
resource "google_cloud_run_service_iam_member" "public_access" {
  role   = "roles/run.invoker"
  member = "allUsers"
}
```

## 🚨 Troubleshooting

### Common Issues

1. **API Not Enabled**
   ```
   Error: googleapi: Error 403: Cloud Run API has not been used in project
   ```
   **Solution**: The Terraform configuration automatically enables required APIs.

2. **Service Account Already Exists**
   ```
   Error: Error creating service account: googleapi: Error 409: Requested entity already exists
   ```
   **Solution**: Import the existing service account:
   ```bash
   terraform import google_service_account.cloud_run_sa \
     projects/PROJECT_ID/serviceAccounts/smart-chart-deploy@PROJECT_ID.iam.gserviceaccount.com
   ```

3. **Permission Denied**
   ```
   Error: googleapi: Error 403: Permission denied
   ```
   **Solution**: Ensure your account has the necessary permissions to create resources.

### State Management

The Terraform state is stored in GCS bucket `smart-chart-terraform-state` with prefix `terraform/state`. This enables:
- **Team collaboration** - Multiple team members can work with the same infrastructure
- **State locking** - Prevents concurrent modifications
- **State backup** - Automatic versioning and backup

## 🔄 CI/CD Integration

This Terraform configuration is designed to work with GitHub Actions:

1. **Bootstrap** - Creates the Terraform state bucket
2. **Build** - Builds and pushes Docker image to Artifact Registry
3. **Deploy** - Runs `terraform apply` to deploy infrastructure

See `.github/workflows/deploy.yml` for the complete CI/CD pipeline.

## 📚 Additional Resources

- [Terraform Google Provider Documentation](https://registry.terraform.io/providers/hashicorp/google/latest/docs)
- [Google Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Google Artifact Registry Documentation](https://cloud.google.com/artifact-registry/docs)
- [Google IAM Documentation](https://cloud.google.com/iam/docs) 