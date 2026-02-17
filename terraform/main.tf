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

variable "project_id" {
  type        = string
  description = "The GCP Project ID"
}

variable "region" {
  type        = string
  default     = "us-central1"
  description = "The GCP region"
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
