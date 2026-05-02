variable "project_id" {
  description = "GCP project ID — atlasmind-prod / atlasmind-stage / atlasmind-data / atlasmind-shared"
  type        = string
}

variable "env" {
  description = "Environment label"
  type        = string
  validation {
    condition     = contains(["prod", "stage", "data", "shared"], var.env)
    error_message = "env must be one of prod, stage, data, shared."
  }
}

variable "region" {
  description = "Primary region"
  type        = string
  default     = "europe-west1"
}

variable "bq_location" {
  description = "BigQuery multi-region"
  type        = string
  default     = "EU"
}

variable "workspace_domain" {
  description = "Google Workspace domain"
  type        = string
  default     = "atlasmind.ai"
}

variable "agents" {
  description = "Names of all 8 AtlasMind agents"
  type        = list(string)
  default = [
    "geopolitical",
    "market",
    "investment",
    "population",
    "technology-trend",
    "country-risk",
    "scenario",
    "strategy-briefing",
  ]
}

variable "image_registry" {
  description = "Artifact Registry path for agent images"
  type        = string
  default     = "europe-west1-docker.pkg.dev/atlasmind-shared/atlasmind"
}

variable "image_tag" {
  description = "Image tag to deploy"
  type        = string
  default     = "latest"
}
