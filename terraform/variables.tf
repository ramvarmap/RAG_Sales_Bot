# variables.tf

variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP region for resources"
  type        = string
  default     = "us-central1"
}

variable "container_image" {
  description = "Docker image URL for the Cloud Run service (e.g., gcr.io/PROJECT_ID/smart-chart:latest)"
  type        = string
}

variable "oracle_username" {
  description = "Oracle database username"
  type        = string
}

variable "oracle_password" {
  description = "Oracle database password"
  type        = string
  sensitive   = true
}

variable "oracle_host" {
  description = "Oracle database host (IP address or hostname)"
  type        = string
}

variable "oracle_port" {
  description = "Oracle database port"
  type        = string
  default     = "1521"
}

variable "oracle_service_name" {
  description = "Oracle database service name"
  type        = string
} 