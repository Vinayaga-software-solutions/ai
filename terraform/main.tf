terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Enable necessary APIs for building and storing images
resource "google_project_service" "cloudbuild" {
  service                    = "cloudbuild.googleapis.com"
  disable_dependent_services = false
  disable_on_destroy         = false
}

resource "google_project_service" "artifactregistry" {
  service                    = "artifactregistry.googleapis.com"
  disable_dependent_services = false
  disable_on_destroy         = false
}

# Create an Artifact Registry repository for our Docker images
resource "google_artifact_registry_repository" "app_repo" {
  location      = var.region
  repository_id = "app-repo"
  description   = "Docker repository for Laravel and other apps"
  format        = "DOCKER"
  depends_on    = [google_project_service.artifactregistry]
}

# Grant permissions to the Service Account that runs the build
resource "google_project_iam_member" "cloud_build_log_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:911593594446-compute@developer.gserviceaccount.com"
}

resource "google_project_iam_member" "cloud_build_artifact_admin" {
  project = var.project_id
  role    = "roles/artifactregistry.repoAdmin"
  member  = "serviceAccount:911593594446-compute@developer.gserviceaccount.com"
}

module "raw_storage" {
  source      = "./modules/storage"
  bucket_name = "tensrgrid-raw-data"
  location    = var.region
}

module "mysql_db" {
  source = "./modules/database"
  zone   = "${var.region}-a"
}

module "pubsub_messaging" {
  source     = "./modules/pubsub"
  topic_name = "tensrgrid-data-file-uploaded"
}

module "laravel_app" {
  source        = "./modules/cloudrun"
  project_id    = var.project_id
  region        = var.region
  service_name  = "tensrgrid-control-plane"
  image         = var.app_image
  env_file_path = "${path.module}/../control-plane/.env"
  db_host       = module.mysql_db.instance_public_ip
  app_key       = var.app_key
}

variable "project_id" {
  type        = string
  description = "The GCP Project ID"
}

variable "region" {
  type        = string
  default     = "us-central1"
  description = "The GCP region"
}

variable "app_image" {
  type        = string
  description = "The Docker image for the Laravel application"
}

variable "app_key" {
  type        = string
  description = "The Laravel APP_KEY"
}

output "storage_bucket_url" {
  value = module.raw_storage.bucket_url
}

output "database_ip" {
  value = module.mysql_db.instance_public_ip
}

output "pubsub_topic" {
  value = module.pubsub_messaging.topic_id
}

output "pubsub_subscription" {
  value = module.pubsub_messaging.subscription_id
}

output "app_url" {
  value = module.laravel_app.service_url
}
