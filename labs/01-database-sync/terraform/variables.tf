variable "project_id" {
  type        = string
  description = "Explicit lab project; never use the active gcloud default."
  nullable    = false

  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{4,28}[a-z0-9]$", var.project_id)) && var.project_id != "nakamalabsio"
    error_message = "Use a valid lab project ID other than nakamalabsio."
  }
}

variable "region" {
  type    = string
  default = "us-central1"
}

variable "zone" {
  type    = string
  default = "us-central1-a"
}
