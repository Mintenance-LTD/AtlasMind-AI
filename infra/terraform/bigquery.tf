locals {
  datasets = {
    atlasmind_warehouse = "Normalised analytical tables"
    atlasmind_claims    = "Every emitted agent claim"
    atlasmind_runs      = "Run metadata"
    atlasmind_scores    = "Score history"
    atlasmind_eval      = "Eval golden sets and run scores"
    atlasmind_audit_logs = "Sink for project audit logs"
  }
}

resource "google_bigquery_dataset" "ds" {
  for_each   = local.datasets
  dataset_id = each.key
  location   = var.bq_location
  project    = var.project_id

  labels = {
    app         = "atlasmind"
    env         = var.env
    cost_center = "atlasmind"
    data_class  = each.key == "atlasmind_audit_logs" ? "restricted" : "public"
  }

  description = each.value

  depends_on = [google_project_service.enabled]
}
