# main.tf

provider "google" {
  project = var.project_id
  region  = var.region
}

# Artifact Registry for Docker images (already exists)
data "google_artifact_registry_repository" "smart_chart" {
  location      = var.region
  repository_id = "smart-chart-repo"
}

# Use existing service account (already exists)
data "google_service_account" "cloud_run_sa" {
  account_id = "smart-chart-deploy"
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
        # Google AI config
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
        # App config
        env {
          name  = "TARGET_CHUNK_SIZE"
          value = "1500"
        }
        env {
          name  = "MAX_CHUNK_SIZE"
          value = "2000"
        }
        env {
          name  = "OVERLAP_SIZE"
          value = "200"
        }
        env {
          name  = "MIN_CHUNK_SIZE"
          value = "500"
        }
        env {
          name  = "DOCUMENT_SIZE_LIMIT"
          value = "256000"
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
}