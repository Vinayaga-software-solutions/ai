# Enable Secret Manager API
resource "google_project_service" "secretmanager" {
  service                    = "secretmanager.googleapis.com"
  disable_dependent_services = false
  disable_on_destroy         = false
}

# Create a secret for the .env file
resource "google_secret_manager_secret" "app_env" {
  secret_id = "${var.service_name}-env-v2" # Using a new ID to ensure clean creation
  
  replication {
    automatic = true
  }

  depends_on = [google_project_service.secretmanager]
}

# Add the .env content to the secret
resource "google_secret_manager_secret_version" "app_env_version" {
  secret      = google_secret_manager_secret.app_env.id
  secret_data = file(var.env_file_path)
}

# Create a service account for Cloud Run
resource "google_service_account" "cloud_run_sa" {
  account_id   = "${var.service_name}-sa"
  display_name = "Service Account for ${var.service_name}"
}

# Grant the service account access to the secret
resource "google_secret_manager_secret_iam_member" "secret_access" {
  secret_id = google_secret_manager_secret.app_env.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

# Cloud Run Service
resource "google_cloud_run_v2_service" "laravel" {
  name     = var.service_name
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    labels = {
      "redeploy-trigger" = formatdate("YYYY-MM-DD-hh-mm-ss", timestamp())
    }
    service_account = google_service_account.cloud_run_sa.email

    containers {
      image = var.image
      
      ports {
        container_port = 8080
      }

      env {
        name  = "DB_HOST"
        value = var.db_host
      }
      
      env {
        name  = "APP_ENV"
        value = "production"
      }

      env {
        name  = "APP_DEBUG"
        value = "true"
      }

      env {
        name  = "APP_KEY"
        value = var.app_key
      }

      volume_mounts {
        name       = "env-file"
        mount_path = "/var/www/html/.env"
      }
    }

    volumes {
      name = "env-file"
      secret {
        secret       = google_secret_manager_secret.app_env.secret_id
        items {
          version = "latest"
          path    = ".env"
        }
      }
    }
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  depends_on = [google_secret_manager_secret_iam_member.secret_access]
}

# Allow unauthenticated access
resource "google_cloud_run_service_iam_member" "public_access" {
  location = google_cloud_run_v2_service.laravel.location
  project  = google_cloud_run_v2_service.laravel.project
  service  = google_cloud_run_v2_service.laravel.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
