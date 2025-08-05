#!/bin/bash

# =============================================================================
# Smart Chart RAG Application - Bootstrap Script
# =============================================================================
# This script creates foundational infrastructure needed before Terraform runs
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

# Function to check if resource exists
resource_exists() {
    local resource_type=$1
    local resource_name=$2
    
    case $resource_type in
        "bucket")
            gsutil ls -b "gs://$resource_name" >/dev/null 2>&1
            ;;
        "service-account")
            gcloud iam service-accounts describe "$resource_name" >/dev/null 2>&1
            ;;
        "repository")
            gcloud artifacts repositories describe "$resource_name" --location="$REGION" >/dev/null 2>&1
            ;;
        "api")
            gcloud services list --enabled --filter="name:$resource_name" --format="value(name)" | grep -q "$resource_name"
            ;;
        *)
            return 1
            ;;
    esac
}

# Function to enable Google Cloud APIs
enable_apis() {
    print_status "Enabling required Google Cloud APIs..."
    
    # All required APIs for the application
    local apis=(
        "storage.googleapis.com"           # For GCS bucket
        "iam.googleapis.com"              # For service accounts
        "artifactregistry.googleapis.com" # For Docker registry
        "run.googleapis.com"              # For Cloud Run
        "aiplatform.googleapis.com"       # For Vertex AI
    )
    
    for api in "${apis[@]}"; do
        print_status "Enabling API: $api"
        
        if resource_exists "api" "$api"; then
            print_warning "API $api is already enabled"
        else
            if gcloud services enable "$api" --project="$PROJECT_ID" --quiet; then
                print_success "Enabled API: $api"
            else
                print_error "Failed to enable API: $api"
                exit 1
            fi
        fi
    done
}

# Function to create GCS bucket for Terraform state
create_terraform_bucket() {
    local bucket_name="smart-chart-terraform-state"
    
    print_status "Creating GCS bucket for Terraform state..."
    
    if resource_exists "bucket" "$bucket_name"; then
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

# Function to create service account
create_service_account() {
    local sa_name="smart-chart-deploy"
    local sa_email="$sa_name@$PROJECT_ID.iam.gserviceaccount.com"
    
    print_status "Creating service account for deployment..."
    
    if resource_exists "service-account" "$sa_email"; then
        print_warning "Service account $sa_email already exists"
        return 0
    fi
    
    if gcloud iam service-accounts create "$sa_name" \
        --display-name="Smart Chart RAG Deployment Service Account" \
        --description="Service account for Smart Chart RAG application deployment"; then
        print_success "Created service account: $sa_email"
    else
        print_error "Failed to create service account"
        exit 1
    fi
}

# Function to assign IAM roles to service account
assign_iam_roles() {
    local sa_email="smart-chart-deploy@$PROJECT_ID.iam.gserviceaccount.com"
    
    print_status "Assigning IAM roles to service account..."
    
    # All required roles for the application
    local roles=(
        # Bootstrap and Terraform operations
        "roles/storage.objectAdmin"      # For Terraform state management
        "roles/iam.serviceAccountUser"  # For Cloud Run service account usage
        "roles/artifactregistry.writer" # For Docker image uploads
        
        # Application runtime permissions
        "roles/aiplatform.user"         # For Vertex AI model access (embeddings + LLM)
        "roles/run.developer"           # For Cloud Run deployment and management
        "roles/run.invoker"             # For Cloud Run service invocation (public access)
    )
    
    for role in "${roles[@]}"; do
        print_status "Assigning role: $role"
        
        if gcloud projects add-iam-policy-binding "$PROJECT_ID" \
            --member="serviceAccount:$sa_email" \
            --role="$role" \
            --quiet; then
            print_success "Assigned role: $role"
        else
            print_warning "Failed to assign role: $role (may already be assigned)"
        fi
    done
}

# Function to create Artifact Registry repository
create_artifact_registry() {
    local repo_name="smart-chart-repo"
    
    print_status "Creating Artifact Registry repository..."
    
    if resource_exists "repository" "$repo_name"; then
        print_warning "Artifact Registry repository $repo_name already exists"
        return 0
    fi
    
    if gcloud artifacts repositories create "$repo_name" \
        --repository-format=docker \
        --location="$REGION" \
        --description="Docker repository for Smart Chart RAG application"; then
        print_success "Created Artifact Registry repository: $repo_name"
    else
        print_error "Failed to create Artifact Registry repository"
        exit 1
    fi
}

# Function to create service account key
create_service_account_key() {
    local sa_email="smart-chart-deploy@$PROJECT_ID.iam.gserviceaccount.com"
    local key_file="smart-chart-deploy-key.json"
    
    print_status "Creating service account key..."
    
    if [ -f "$key_file" ]; then
        print_warning "Service account key already exists: $key_file"
        return 0
    fi
    
    if gcloud iam service-accounts keys create "$key_file" \
        --iam-account="$sa_email"; then
        print_success "Created service account key: $key_file"
        print_warning "⚠️  Keep this key secure and never commit it to version control!"
        print_warning "⚠️  Update your GitHub repository secret 'GCP_SA_KEY' with this key!"
    else
        print_error "Failed to create service account key"
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
    echo "   • Service Account: smart-chart-deploy@$PROJECT_ID.iam.gserviceaccount.com"
    echo "   • Artifact Registry: smart-chart-repo"
    echo "   • Service Account Key: smart-chart-deploy-key.json"
    echo
    echo "🔧 Enabled APIs:"
    echo "   • storage.googleapis.com"
    echo "   • iam.googleapis.com"
    echo "   • artifactregistry.googleapis.com"
    echo "   • run.googleapis.com"
    echo "   • aiplatform.googleapis.com"
    echo
    echo "🔑 Assigned IAM Roles:"
    echo "   • roles/storage.objectAdmin (Terraform state management)"
    echo "   • roles/iam.serviceAccountUser (Cloud Run service account usage)"
    echo "   • roles/artifactregistry.writer (Docker image uploads)"
    echo "   • roles/aiplatform.user (Vertex AI model access)"
    echo "   • roles/run.developer (Cloud Run deployment)"
    echo "   • roles/run.invoker (Cloud Run service invocation)"
    echo
    echo "🔧 Next steps:"
    echo "   1. Update GitHub repository secret 'GCP_SA_KEY' with the service account key"
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
    echo "🚀 Smart Chart RAG Application - Bootstrap Script"
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
    
    # Create foundational infrastructure
    enable_apis
    create_terraform_bucket
    create_service_account
    assign_iam_roles
    create_artifact_registry
    create_service_account_key
    
    # Display summary
    display_summary
}

# Run main function
main "$@" 