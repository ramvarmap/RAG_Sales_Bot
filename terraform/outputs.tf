# =============================================================================
# Smart Chart RAG Application - Terraform Outputs
# =============================================================================

output "cloud_run_service_url" {
  description = "URL of the deployed Cloud Run service"
  value       = google_cloud_run_service.smart_chart.status[0].url
}

output "service_account_email" {
  description = "Email of the service account used by Cloud Run"
  value       = google_service_account.cloud_run_sa.email
}

output "artifact_registry_location" {
  description = "Location of the Artifact Registry repository"
  value       = google_artifact_registry_repository.smart_chart.location
}

output "artifact_registry_name" {
  description = "Name of the Artifact Registry repository"
  value       = google_artifact_registry_repository.smart_chart.name
}

output "project_id" {
  description = "Project ID where resources are deployed"
  value       = var.project_id
}

output "region" {
  description = "Region where resources are deployed"
  value       = var.region
} 