#!/bin/bash

# =============================================================================
# Smart Chart RAG Application - Minimal Bootstrap Script
# =============================================================================
# This script creates ONLY the GCS bucket for Terraform state
# All other infrastructure is managed by Terraform
# =============================================================================

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to validate required tools
validate_prerequisites() {
    print_status "Validating prerequisites..."
    
    if ! command_exists gcloud; then
        print_error "gcloud CLI is not installed. Please install it first."
        exit 1
    fi
    
    if ! command_exists gsutil; then
        print_error "gsutil is not available. Please install gcloud CLI properly."
        exit 1
    fi
    
    print_success "Prerequisites validation passed"
}

# Function to get project ID
get_project_id() {
    local project_id
    
    # Try to get from gcloud config
    project_id=$(gcloud config get-value project 2>/dev/null || echo "")
    
    if [ -z "$project_id" ]; then
        print_error "No project ID found in gcloud config."
        print_status "Please run: gcloud config set project YOUR_PROJECT_ID"
        exit 1
    fi
    
    echo "$project_id"
}

# Function to get region
get_region() {
    local region
    
    # Try to get from gcloud config
    region=$(gcloud config get-value compute/region 2>/dev/null || echo "")
    
    if [ -z "$region" ]; then
        print_warning "No region found in gcloud config. Using default: us-central1"
        region="us-central1"
    fi
    
    echo "$region"
}

# Function to check if bucket exists
bucket_exists() {
    local bucket_name=$1
    gsutil ls -b "gs://$bucket_name" >/dev/null 2>&1
}

# Function to create GCS bucket for Terraform state
create_terraform_bucket() {
    local bucket_name="smart-chart-terraform-state"
    
    print_status "Creating GCS bucket for Terraform state..."
    
    if bucket_exists "$bucket_name"; then
        print_warning "Bucket gs://$bucket_name already exists"
        return 0
    fi
    
    if gsutil mb -p "$PROJECT_ID" -c STANDARD -l "$REGION" "gs://$bucket_name"; then
        print_success "Created GCS bucket: gs://$bucket_name"
        
        # Set bucket versioning for safety
        gsutil versioning set on "gs://$bucket_name"
        print_success "Enabled versioning on bucket"
    else
        print_error "Failed to create GCS bucket"
        exit 1
    fi
}

# Function to display summary
display_summary() {
    echo
    print_success "🎉 Bootstrap completed successfully!"
    echo
    echo "📦 Created resources:"
    echo "   • GCS Bucket: gs://smart-chart-terraform-state"
    echo
    echo "🔧 Next steps:"
    echo "   1. Create terraform.tfvars file with your configuration"
    echo "   2. Run: terraform init"
    echo "   3. Run: terraform plan"
    echo "   4. Run: terraform apply"
    echo
    echo "📚 For detailed instructions, see: GCP_DEPLOYMENT_GUIDE.md"
    echo
}

# Function to handle cleanup on script exit
cleanup() {
    if [ $? -ne 0 ]; then
        print_error "Bootstrap script failed. Please check the errors above."
        exit 1
    fi
}

# Set trap for cleanup
trap cleanup EXIT

# Main execution
main() {
    echo "============================================================================="
    echo "🚀 Smart Chart RAG Application - Minimal Bootstrap Script"
    echo "============================================================================="
    echo
    
    # Validate prerequisites
    validate_prerequisites
    
    # Get project configuration
    PROJECT_ID=$(get_project_id)
    REGION=$(get_region)
    
    print_status "Using Project ID: $PROJECT_ID"
    print_status "Using Region: $REGION"
    echo
    
    # Create only the Terraform state bucket
    create_terraform_bucket
    
    # Display summary
    display_summary
}

# Run main function
main "$@" 