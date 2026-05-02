locals {
  enabled_apis = [
    "aiplatform.googleapis.com",
    "discoveryengine.googleapis.com",
    "run.googleapis.com",
    "cloudfunctions.googleapis.com",
    "cloudscheduler.googleapis.com",
    "pubsub.googleapis.com",
    "bigquery.googleapis.com",
    "firestore.googleapis.com",
    "firebase.googleapis.com",
    "firebasehosting.googleapis.com",
    "identitytoolkit.googleapis.com",
    "storage.googleapis.com",
    "artifactregistry.googleapis.com",
    "cloudbuild.googleapis.com",
    "secretmanager.googleapis.com",
    "iap.googleapis.com",
    "docs.googleapis.com",
    "slides.googleapis.com",
    "sheets.googleapis.com",
    "drive.googleapis.com",
    "earthengine.googleapis.com",
    "youtube.googleapis.com",
    "logging.googleapis.com",
    "monitoring.googleapis.com",
    "cloudtrace.googleapis.com",
  ]
}

resource "google_project_service" "enabled" {
  for_each                   = toset(local.enabled_apis)
  project                    = var.project_id
  service                    = each.value
  disable_dependent_services = false
  disable_on_destroy         = false
}
