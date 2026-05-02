resource "google_artifact_registry_repository" "atlasmind" {
  count         = var.env == "shared" ? 1 : 0
  location      = var.region
  repository_id = "atlasmind"
  description   = "AtlasMind container images"
  format        = "DOCKER"
  project       = var.project_id

  depends_on = [google_project_service.enabled]
}
