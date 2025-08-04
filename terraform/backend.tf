# backend.tf

terraform {
  backend "gcs" {
    bucket = "smart-chart-terraform-state"
    prefix = "terraform/state"
  }
} 