# Scheduled ingest jobs. Each one publishes to Pub/Sub which triggers a Cloud
# Run job (defined separately) for the loader.

locals {
  ingest_schedule = {
    sanctions     = { cron = "0 * * * *",  source = "ofac_eu_uk" }
    market_eod    = { cron = "30 22 * * *", source = "fx_equities_eod" }
    gdelt         = { cron = "15 * * * *", source = "gdelt" }
    google_trends = { cron = "0 4 * * 1",  source = "google_trends" }
    earth_engine  = { cron = "0 5 1 * *",  source = "earth_engine" }
    imf_weo       = { cron = "0 6 * * 0",  source = "imf_weo" }
    un_wpp        = { cron = "0 7 1 1 *",  source = "un_wpp" }
    wgi           = { cron = "0 8 1 1 *",  source = "world_bank_wgi" }
  }
}

resource "google_cloud_scheduler_job" "ingest" {
  for_each = local.ingest_schedule
  name     = "ingest-${each.key}"
  schedule = each.value.cron
  region   = var.region
  project  = var.project_id

  pubsub_target {
    topic_name = google_pubsub_topic.topics["runs.requested"].id
    data       = base64encode(jsonencode({
      kind   = "ingest"
      source = each.value.source
    }))
  }

  depends_on = [google_pubsub_topic.topics]
}
