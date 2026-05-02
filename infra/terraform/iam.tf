# Service accounts for the conductor and each agent.

resource "google_service_account" "conductor" {
  account_id   = "conductor-sa"
  display_name = "AtlasMind Strategy Conductor"
  project      = var.project_id
}

resource "google_service_account" "agents" {
  for_each     = toset(var.agents)
  account_id   = "agent-${each.value}-sa"
  display_name = "AtlasMind ${each.value} Agent"
  project      = var.project_id
}

resource "google_service_account" "ingest" {
  account_id   = "ingest-sa"
  display_name = "AtlasMind Ingestion"
  project      = var.project_id
}

resource "google_service_account" "api" {
  account_id   = "api-sa"
  display_name = "AtlasMind API Gateway"
  project      = var.project_id
}

resource "google_service_account" "briefing" {
  account_id   = "briefing-sa"
  display_name = "AtlasMind Briefing (Workspace Docs/Slides)"
  project      = var.project_id
}

# Custom role for end users invoking runs from the dashboard.
resource "google_project_iam_custom_role" "run_user" {
  role_id     = "atlasmindRunUser"
  title       = "AtlasMind Run User"
  description = "Can invoke briefings via the AtlasMind API"
  project     = var.project_id
  permissions = [
    "run.routes.invoke",
    "iap.tunnelInstances.accessViaIAP",
  ]
}

# Bind groups (set in GCP_SETUP.md).
resource "google_project_iam_member" "analysts" {
  project = var.project_id
  role    = google_project_iam_custom_role.run_user.id
  member  = "group:analysts@${var.workspace_domain}"
}

resource "google_project_iam_member" "sec_viewers" {
  project = var.project_id
  role    = "roles/iam.securityReviewer"
  member  = "group:sec@${var.workspace_domain}"
}
