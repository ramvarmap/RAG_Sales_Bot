# =============================================================================
# Smart Chart RAG Application - Terraform Configuration
# =============================================================================
# This configuration provisions application infrastructure
# Service account and IAM roles are created by bootstrap script
# =============================================================================

# Configure the Google Cloud Provider
provider "google" {
  project = var.project_id
  region  = var.region
}

# Enable required Google Cloud APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "storage.googleapis.com",           # For GCS bucket
    "iam.googleapis.com",              # For service accounts
    "artifactregistry.googleapis.com", # For Docker registry
    "run.googleapis.com",              # For Cloud Run
    "aiplatform.googleapis.com"        # For Vertex AI
  ])
  
  project = var.project_id
  service = each.value
  
  disable_dependent_services = false
  disable_on_destroy         = false
}

# Use existing service account (created by bootstrap script)
data "google_service_account" "cloud_run_sa" {
  account_id = "smart-chart-deploy"
  
  depends_on = [google_project_service.required_apis]
}

# Create Artifact Registry repository
resource "google_artifact_registry_repository" "smart_chart" {
  location      = var.region
  repository_id = "smart-chart-repo"
  description   = "Docker repository for Smart Chart RAG application"
  format        = "DOCKER"
  
  depends_on = [google_project_service.required_apis]
}

# Cloud Run service
resource "google_cloud_run_service" "smart_chart" {
  name     = "smart-chart-rag"
  location = var.region

  template {
    spec {
      service_account_name = data.google_service_account.cloud_run_sa.email
      containers {
        image = var.container_image
        ports {
          container_port = 8080
        }
        
        # Oracle DB connection env vars
        env {
          name  = "ORACLE_USERNAME"
          value = var.oracle_username
        }
        env {
          name  = "ORACLE_PASSWORD"
          value = var.oracle_password
        }
        env {
          name  = "ORACLE_HOST"
          value = var.oracle_host
        }
        env {
          name  = "ORACLE_PORT"
          value = var.oracle_port
        }
        env {
          name  = "ORACLE_SERVICE_NAME"
          value = var.oracle_service_name
        }
        
        # Google Cloud settings
        env {
          name  = "VERTEX_PROJECT_ID"
          value = var.project_id
        }
        env {
          name  = "VERTEX_LOCATION"
          value = var.region
        }
        env {
          name  = "VERTEX_EMBEDDING_MODEL"
          value = "text-embedding-005"
        }
        env {
          name  = "GOOGLE_APPLICATION_CREDENTIALS"
          value = "/app/gcp_secrets/llama-sa-key.json"
        }
        
        resources {
          limits = {
            cpu    = "2000m"
            memory = "4Gi"
          }
        }
      }
    }
  }
  
  autogenerate_revision_name = true
  
  traffic {
    percent         = 100
    latest_revision = true
  }
  
  depends_on = [
    data.google_service_account.cloud_run_sa,
    google_project_service.required_apis
  ]
}

# Make Cloud Run service publicly accessible
resource "google_cloud_run_service_iam_member" "public_access" {
  location = google_cloud_run_service.smart_chart.location
  service  = google_cloud_run_service.smart_chart.name
  role     = "roles/run.invoker"
  member   = "allUsers"
  
  depends_on = [google_cloud_run_service.smart_chart]
}