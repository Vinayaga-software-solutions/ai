variable "bucket_name" {
  type        = string
  description = "The name of the GCS bucket"
}

variable "location" {
  type        = string
  default     = "US"
  description = "The GCS location"
}
