variable "project_id" {
  type        = string
  description = "The GCP Project ID"
}

variable "region" {
  type        = string
  description = "The GCP region"
}

variable "service_name" {
  type        = string
  description = "The name of the Cloud Run service"
  default     = "laravel-app"
}

variable "image" {
  type        = string
  description = "The Docker image to deploy"
}

variable "env_file_path" {
  type        = string
  description = "Path to the local .env file"
}

variable "db_host" {
  type        = string
  description = "IP address of the database"
}

variable "app_key" {
  type        = string
  description = "Laravel APP_KEY"
}
