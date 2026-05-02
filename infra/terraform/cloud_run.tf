# One Cloud Run service per agent + the Strategy Conductor + the API gateway.

resource "google_cloud_run_v2_service" "agents" {
  for_each = toset(var.agents)
  name     = "atlasmind-agent-${each.value}"
  location = var.region
  project  = var.project_id

  ingress = "INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER"

  template {
    service_account = google_service_account.agents[each.value].email
    containers {
      image = "${var.image_registry}/${each.value}:${var.image_tag}"
      ports { container_port = 8080 }
      env {
        name  = "ATLASMIND_ENV"
        value = var.env
      }
      env {
        name  = "GOOGLE_CLOUD_PROJECT"
        value = var.project_id
      }
      env {
        name  = "VERTEX_LOCATION"
        value = var.region
      }
      resources {
        limits = {
          cpu    = "2"
          memory = "2Gi"
        }
      }
    }
    scaling {
      min_instance_count = 0
      max_instance_count = 10
    }
  }

  labels = {
    app         = "atlasmind"
    env         = var.env
    agent       = each.value
    cost_center = "atlasmind"
  }

  depends_on = [google_project_service.enabled]
}

resource "google_cloud_run_v2_service" "conductor" {
  name     = "atlasmind-conductor"
  location = var.region
  project  = var.project_id
  ingress  = "INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER"

  template {
    service_account = google_service_account.conductor.email
    containers {
      image = "${var.image_registry}/conductor:${var.image_tag}"
      ports { container_port = 8080 }
      env {
        name  = "ATLASMIND_ENV"
        value = var.env
      }
    }
    scaling {
      min_instance_count = 0
      max_instance_count = 5
    }
  }

  labels = {
    app         = "atlasmind"
    env         = var.env
    cost_center = "atlasmind"
  }

  depends_on = [google_project_service.enabled]
}

resource "google_cloud_run_v2_service" "api" {
  name     = "atlasmind-api"
  location = var.region
  project  = var.project_id
  ingress  = "INGRESS_TRAFFIC_ALL"  # IAP-protected

  template {
    service_account = google_service_account.api.email
    containers {
      image = "${var.image_registry}/api:${var.image_tag}"
      ports { container_port = 8080 }
    }
    scaling {
      min_instance_count = 1
      max_instance_count = 5
    }
  }

  labels = {
    app         = "atlasmind"
    env         = var.env
    cost_center = "atlasmind"
  }

  depends_on = [google_project_service.enabled]
}
