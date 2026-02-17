# Service Account for PDF Converter
resource "google_service_account" "pdf_converter_sa" {
  account_id   = "pdf-converter-sa"
  display_name = "Service Account for PDF Converter"
}

# Grant Storage permissions to the SA
resource "google_storage_bucket_iam_member" "pdf_converter_storage_admin" {
  bucket = module.raw_storage.bucket_name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.pdf_converter_sa.email}"
}

# Cloud Run Service for PDF Converter
resource "google_cloud_run_v2_service" "pdf_converter" {
  name     = "pdf-converter-service"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    service_account = google_service_account.pdf_converter_sa.email

    containers {
      image = "us-central1-docker.pkg.dev/${var.project_id}/app-repo/pdf-converter:latest"
      
      ports {
        container_port = 8080
      }

      env {
        name  = "GCP_PROJECT_ID"
        value = var.project_id
      }

      env {
        name  = "GCS_BUCKET"
        value = module.raw_storage.bucket_name
      }

      env {
        name  = "OUTPUT_FOLDER"
        value = "tensrgrid/markdown-output"
      }
      
      resources {
        limits = {
          cpu    = "2"
          memory = "2Gi"
        }
      }
    }
    
    scaling {
      max_instance_count = 10
      min_instance_count = 0
    }
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }
}

# Allow Pub/Sub to invoke the service
resource "google_cloud_run_service_iam_member" "pdf_converter_invoker" {
  location = google_cloud_run_v2_service.pdf_converter.location
  project  = google_cloud_run_v2_service.pdf_converter.project
  service  = google_cloud_run_v2_service.pdf_converter.name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.pdf_converter_sa.email}"
}

# Grant Pub/Sub Service Agent permission to create tokens for the PDF Converter SA
resource "google_service_account_iam_member" "pubsub_token_creator" {
  service_account_id = google_service_account.pdf_converter_sa.name
  role               = "roles/iam.serviceAccountTokenCreator"
  member             = "serviceAccount:service-${data.google_project.project.number}@gcp-sa-pubsub.iam.gserviceaccount.com"
}

# Pub/Sub Push Subscription
resource "google_pubsub_subscription" "pdf_converter_push" {
  name  = "pdf-converter-push-subscription"
  topic = module.pubsub_messaging.topic_id

  push_config {
    push_endpoint = google_cloud_run_v2_service.pdf_converter.uri
    
    oidc_token {
      service_account_email = google_service_account.pdf_converter_sa.email
    }
  }

  ack_deadline_seconds = 300
}

data "google_project" "project" {}

output "pdf_converter_url" {
  value = google_cloud_run_v2_service.pdf_converter.uri
}
