# main.tf

provider "google" {
  project = var.project_id
  region  = var.region
}

# Artifact Registry for Docker images
resource "google_artifact_registry_repository" "smart_chart" {
  location      = var.region
  repository_id = "smart-chart-repo"
  description   = "Docker repository for Smart Chart RAG application"
  format        = "DOCKER"
}

# Service account for Cloud Run
resource "google_service_account" "cloud_run_sa" {
  account_id   = "smart-chart-cloud-run"
  display_name = "Smart Chart Cloud Run Service Account"
  description  = "Service account for Smart Chart RAG application"
}

# IAM roles for the service account
resource "google_project_iam_member" "cloud_run_sa_roles" {
  for_each = toset([
    "roles/aiplatform.user",           # Vertex AI access
    "roles/storage.objectViewer",      # GCS access (if needed)
    "roles/logging.logWriter",         # Cloud Logging
    "roles/monitoring.metricWriter"    # Cloud Monitoring
  ])
  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

# Cloud Run service
resource "google_cloud_run_service" "smart_chart" {
  name     = "smart-chart-rag"
  location = var.region

  template {
    spec {
      service_account_name = google_service_account.cloud_run_sa.email
      containers {
        image = var.container_image
        ports {
          container_port = 8080
        }
        # Oracle DB connection env vars
        env { name = "ORACLE_USERNAME"      value = var.oracle_username }
        env { name = "ORACLE_PASSWORD"      value = var.oracle_password }
        env { name = "ORACLE_HOST"          value = var.oracle_host }
        env { name = "ORACLE_PORT"          value = var.oracle_port }
        env { name = "ORACLE_SERVICE_NAME"  value = var.oracle_service_name }
        # Google AI config
        env { name = "VERTEX_PROJECT_ID"    value = var.project_id }
        env { name = "VERTEX_LOCATION"      value = var.region }
        env { name = "VERTEX_EMBEDDING_MODEL" value = "text-embedding-005" }
        # App config
        env { name = "TARGET_CHUNK_SIZE"    value = "1500" }
        env { name = "MAX_CHUNK_SIZE"       value = "2000" }
        env { name = "OVERLAP_SIZE"         value = "200" }
        env { name = "MIN_CHUNK_SIZE"       value = "500" }
        env { name = "DOCUMENT_SIZE_LIMIT"  value = "256000" }
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

output "cloud_run_url" {
  value = google_cloud_run_service.smart_chart.status[0].url
}

output "cloud_run_service_account" {
  value = google_service_account.cloud_run_sa.email
}