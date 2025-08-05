# outputs.tf

output "cloud_run_url" {
  description = "URL of the deployed Cloud Run service"
  value       = google_cloud_run_service.smart_chart.status[0].url
}

output "cloud_run_service_account" {
  description = "Email of the service account used by Cloud Run"
  value       = data.google_service_account.cloud_run_sa.email
}

output "artifact_registry_location" {
  description = "Location of the Artifact Registry repository"
  value       = data.google_artifact_registry_repository.smart_chart.location
}

output "artifact_registry_name" {
  description = "Name of the Artifact Registry repository"
  value       = data.google_artifact_registry_repository.smart_chart.name
} 