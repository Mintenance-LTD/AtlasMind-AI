locals {
  buckets = {
    "atlasmind-raw"       = { class = "STANDARD", lifecycle_days = 90,  archive = "ARCHIVE" }
    "atlasmind-runs"      = { class = "STANDARD", lifecycle_days = 30,  archive = "COLDLINE" }
    "atlasmind-templates" = { class = "STANDARD", lifecycle_days = 0,   archive = null }
    "atlasmind-build"     = { class = "STANDARD", lifecycle_days = 14,  archive = null }
  }
}

resource "google_storage_bucket" "buckets" {
  for_each                    = local.buckets
  name                        = "${each.key}-${var.env}"
  project                     = var.project_id
  location                    = var.bq_location
  force_destroy               = false
  uniform_bucket_level_access = true
  versioning { enabled = true }

  dynamic "lifecycle_rule" {
    for_each = each.value.lifecycle_days > 0 ? [1] : []
    content {
      action {
        type          = "SetStorageClass"
        storage_class = each.value.archive
      }
      condition {
        age = each.value.lifecycle_days
      }
    }
  }

  labels = {
    app         = "atlasmind"
    env         = var.env
    cost_center = "atlasmind"
  }

  depends_on = [google_project_service.enabled]
}
