# =============================================================================
# Smart Chart RAG Application - Terraform Configuration
# =============================================================================
# This configuration provisions application infrastructure
# APIs, service account, IAM roles, and Artifact Registry are created by bootstrap script
# =============================================================================

# Configure the Google Cloud Provider
provider "google" {
  project = var.project_id
  region  = var.region
}

# Use existing service account (created by bootstrap script)
data "google_service_account" "cloud_run_sa" {
  account_id = "smart-chart-deploy"
}

# Use existing Artifact Registry repository (created by bootstrap script)
data "google_artifact_registry_repository" "smart_chart" {
  location      = var.region
  repository_id = "smart-chart-repo"
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
  
  depends_on = [data.google_service_account.cloud_run_sa]
}

# Make Cloud Run service publicly accessible
resource "google_cloud_run_service_iam_member" "public_access" {
  location = google_cloud_run_service.smart_chart.location
  service  = google_cloud_run_service.smart_chart.name
  role     = "roles/run.invoker"
  member   = "allUsers"
  
  depends_on = [google_cloud_run_service.smart_chart]
}