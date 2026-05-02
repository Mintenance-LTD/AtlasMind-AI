locals {
  topics = [
    "runs.requested",
    "agents.completed",
    "runs.completed",
    "alerts.triggered",
  ]
}

resource "google_pubsub_topic" "topics" {
  for_each = toset(local.topics)
  name     = each.value
  project  = var.project_id

  labels = {
    app         = "atlasmind"
    env         = var.env
    cost_center = "atlasmind"
  }

  depends_on = [google_project_service.enabled]
}

resource "google_pubsub_subscription" "conductor_runs_requested" {
  name    = "conductor-runs-requested"
  topic   = google_pubsub_topic.topics["runs.requested"].name
  project = var.project_id

  ack_deadline_seconds = 60
  retain_acked_messages = false

  expiration_policy { ttl = "" }
}
