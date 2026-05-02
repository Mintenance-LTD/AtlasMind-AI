#!/usr/bin/env bash
# Enable AtlasMind APIs on a project. Run once per project.
#
# Usage:  ./infra/scripts/enable-apis.sh atlasmind-prod

set -euo pipefail
PROJECT="${1:?usage: enable-apis.sh <project-id>}"

APIS=(
  aiplatform.googleapis.com
  discoveryengine.googleapis.com
  run.googleapis.com
  cloudfunctions.googleapis.com
  cloudscheduler.googleapis.com
  pubsub.googleapis.com
  bigquery.googleapis.com
  firestore.googleapis.com
  firebase.googleapis.com
  firebasehosting.googleapis.com
  identitytoolkit.googleapis.com
  storage.googleapis.com
  artifactregistry.googleapis.com
  cloudbuild.googleapis.com
  secretmanager.googleapis.com
  iap.googleapis.com
  docs.googleapis.com
  slides.googleapis.com
  sheets.googleapis.com
  drive.googleapis.com
  earthengine.googleapis.com
  youtube.googleapis.com
  logging.googleapis.com
  monitoring.googleapis.com
  cloudtrace.googleapis.com
)

for api in "${APIS[@]}"; do
  echo "Enabling $api on $PROJECT"
  gcloud services enable "$api" --project="$PROJECT"
done

echo "Done."
