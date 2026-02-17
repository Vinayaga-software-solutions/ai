resource "google_storage_bucket" "raw_data" {
  name          = var.bucket_name
  location      = var.location
  force_destroy = true

  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"

  versioning {
    enabled = true
  }
}

output "bucket_url" {
  value = google_storage_bucket.raw_data.url
}
