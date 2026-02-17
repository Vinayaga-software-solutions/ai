resource "google_pubsub_topic" "data_uploaded" {
  name = var.topic_name
}

resource "google_pubsub_subscription" "pull_subscription" {
  name  = "${var.topic_name}-pull"
  topic = google_pubsub_topic.data_uploaded.name

  # Pull mode is default, but we'll be explicit about ACK deadline
  ack_deadline_seconds = 20

  # Retain messages for 7 days
  message_retention_duration = "604800s"
}

output "topic_id" {
  value = google_pubsub_topic.data_uploaded.id
}

output "subscription_id" {
  value = google_pubsub_subscription.pull_subscription.id
}
