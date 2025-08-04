# Terraform Infrastructure for Smart Chart RAG System

This directory contains Terraform configuration to deploy the Smart Chart RAG application on Google Cloud Platform using Cloud Run.

## 📋 Prerequisites

1. **Google Cloud SDK** installed and configured
2. **Terraform** (version >= 1.0) installed
3. **GCP Project** with billing enabled
4. **Oracle 23c AI Database** running on a remote server
5. **Docker image** built and pushed to Artifact Registry

## 🏗️ Resources Created

- **Artifact Registry Repository**: For storing Docker images
- **Service Account**: For Cloud Run with necessary IAM permissions
- **Cloud Run Service**: The main application deployment
- **IAM Bindings**: Required permissions for the service account

## 🚀 Quick Start

### 1. Create GCS Bucket for Terraform State

```bash
# Create the bucket for Terraform state (run this once)
gsutil mb -l us-central1 gs://smart-chart-terraform-state
```

### 2. Initialize Terraform

```bash
cd terraform
terraform init
```

### 3. Plan the Deployment

```bash
terraform plan \
  -var="project_id=YOUR_PROJECT_ID" \
  -var="region=us-central1" \
  -var="container_image=gcr.io/YOUR_PROJECT_ID/smart-chart:latest" \
  -var="oracle_username=YOUR_DB_USER" \
  -var="oracle_password=YOUR_DB_PASSWORD" \
  -var="oracle_host=YOUR_DB_HOST_IP" \
  -var="oracle_port=1521" \
  -var="oracle_service_name=YOUR_DB_SERVICE_NAME"
```

### 4. Apply the Configuration

```bash
terraform apply \
  -var="project_id=YOUR_PROJECT_ID" \
  -var="region=us-central1" \
  -var="container_image=gcr.io/YOUR_PROJECT_ID/smart-chart:latest" \
  -var="oracle_username=YOUR_DB_USER" \
  -var="oracle_password=YOUR_DB_PASSWORD" \
  -var="oracle_host=YOUR_DB_HOST_IP" \
  -var="oracle_port=1521" \
  -var="oracle_service_name=YOUR_DB_SERVICE_NAME"
```

## 🔧 Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `project_id` | GCP Project ID | Yes | - |
| `region` | GCP region for resources | No | `us-central1` |
| `container_image` | Docker image URL | Yes | - |
| `oracle_username` | Oracle DB username | Yes | - |
| `oracle_password` | Oracle DB password | Yes | - |
| `oracle_host` | Oracle DB host IP/hostname | Yes | - |
| `oracle_port` | Oracle DB port | No | `1521` |
| `oracle_service_name` | Oracle DB service name | Yes | - |

## 📊 Outputs

After successful deployment, Terraform will output:

- **cloud_run_url**: URL to access your application
- **cloud_run_service_account**: Service account email used by Cloud Run
- **artifact_registry_location**: Location of the Docker repository
- **artifact_registry_name**: Name of the Docker repository

## 🔄 Updating the Deployment

### Update Container Image

```bash
terraform apply \
  -var="container_image=gcr.io/YOUR_PROJECT_ID/smart-chart:NEW_TAG" \
  # ... other variables
```

### Update Environment Variables

Modify the `main.tf` file and reapply:

```bash
terraform apply # ... with your variables
```

## 🧹 Cleanup

To destroy all resources:

```bash
terraform destroy # ... with your variables
```

## 🔒 Security Notes

1. **Oracle Database**: Ensure your Oracle DB allows connections from Cloud Run's IP ranges
2. **Passwords**: Never commit passwords to version control
3. **Service Account**: The created service account has minimal required permissions
4. **State File**: Terraform state is stored securely in GCS

## 🐛 Troubleshooting

### Common Issues

1. **Permission Denied**: Ensure your GCP account has necessary permissions
2. **Database Connection**: Verify Oracle DB is accessible from Cloud Run
3. **Image Not Found**: Ensure Docker image is pushed to Artifact Registry
4. **State Lock**: If Terraform hangs, check for state locks in GCS

### Debug Commands

```bash
# Check Terraform version
terraform version

# Validate configuration
terraform validate

# Show current state
terraform show

# List resources
terraform state list
```

## 📞 Support

For issues related to:
- **Terraform**: Check the [Terraform documentation](https://www.terraform.io/docs)
- **Cloud Run**: Check the [Cloud Run documentation](https://cloud.google.com/run/docs)
- **Oracle DB**: Ensure network connectivity and firewall rules 