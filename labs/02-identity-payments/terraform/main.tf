variable "project_id" {
  type        = string
  description = "Explicit lab project; never use the active gcloud default."
  nullable    = false

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{4,28}[a-z0-9]$", var.project_id)) && var.project_id != "nakamalabsio"
    error_message = "Use a valid lab project ID other than nakamalabsio."
  }
}

resource "google_project_service" "pubsub" {
  project            = var.project_id
  service            = "pubsub.googleapis.com"
  disable_on_destroy = false
}

resource "google_pubsub_topic" "notifications" {
  name       = "pca-payment-notifications"
  depends_on = [google_project_service.pubsub]
}

resource "google_pubsub_subscription" "local_observer" {
  name                       = "pca-payment-notifications-observer"
  topic                      = google_pubsub_topic.notifications.id
  ack_deadline_seconds       = 20
  message_retention_duration = "86400s"
}

output "notification_topic" {
  value = google_pubsub_topic.notifications.id
}

output "observer_subscription" {
  value = google_pubsub_subscription.local_observer.id
}
