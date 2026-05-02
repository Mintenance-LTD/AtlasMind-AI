output "project_id" {
  value = var.project_id
}

output "agent_services" {
  value = {
    for k, s in google_cloud_run_v2_service.agents : k => s.uri
  }
}

output "conductor_url" {
  value = google_cloud_run_v2_service.conductor.uri
}

output "api_url" {
  value = google_cloud_run_v2_service.api.uri
}

output "datasets" {
  value = [for d in google_bigquery_dataset.ds : d.dataset_id]
}
