locals {
  secret_names = [
    "oauth_client_id",
    "oauth_client_secret",
    "youtube_api_key",
    "maps_platform_api_key",
    "acled_api_key",
  ]
}

resource "google_secret_manager_secret" "secrets" {
  for_each  = toset(local.secret_names)
  secret_id = each.value
  project   = var.project_id

  replication { auto {} }

  labels = {
    app         = "atlasmind"
    env         = var.env
    cost_center = "atlasmind"
  }

  depends_on = [google_project_service.enabled]
}
