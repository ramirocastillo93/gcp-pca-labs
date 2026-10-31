variable "project_id" {
  description = "Explicit GCP lab project ID. Never use the active gcloud default."
  type        = string
  nullable    = false

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{4,28}[a-z0-9]$", var.project_id)) && var.project_id != "nakamalabsio"
    error_message = "Use a 6-30 character lab project ID other than nakamalabsio."
  }
}
