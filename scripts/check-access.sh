#!/usr/bin/env bash
# Do not allow inherited shell tracing to expose the ADC token.
set +x
set -euo pipefail

usage() {
  printf 'Usage: %s (reads GCP_PROJECT_ID from .env)\n' "${0##*/}" >&2
}

if [[ $# -ne 0 ]]; then
  usage
  exit 2
fi

repo_root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
env_file=$repo_root/.env
if [[ ! -f $env_file ]]; then
  printf 'Missing .env. Copy .env.example to .env and set GCP_PROJECT_ID.\n' >&2
  exit 2
fi

project_id=
project_id_seen=false
while IFS= read -r line || [[ -n $line ]]; do
  line=${line%$'\r'}
  case $line in
    GCP_PROJECT_ID=*)
      if [[ $project_id_seen == true ]]; then
        printf 'GCP_PROJECT_ID appears more than once in .env.\n' >&2
        exit 2
      fi
      project_id=${line#GCP_PROJECT_ID=}
      project_id_seen=true
      ;;
  esac
done < "$env_file"

if [[ ! $project_id =~ ^[a-z][a-z0-9-]{4,28}[a-z0-9]$ || $project_id == nakamalabsio ]]; then
  printf 'Invalid GCP_PROJECT_ID in .env. Set a 6-30 character lab project ID other than nakamalabsio.\n' >&2
  exit 2
fi

if ! command -v gcloud >/dev/null 2>&1; then
  printf 'Google Cloud CLI (gcloud) is unavailable.\n' >&2
  exit 1
fi

# Both project reads name the target explicitly; neither uses the CLI default project.
if ! found_project=$(gcloud projects describe "$project_id" --project="$project_id" --format='value(projectId)' 2>/dev/null); then
  printf 'Cannot read project %s with the current gcloud CLI credentials.\n' "$project_id" >&2
  printf 'For the exact cause, run: gcloud projects describe %s --project=%s\n' "$project_id" "$project_id" >&2
  printf 'If gcloud reports expired authentication, run gcloud auth login in an interactive terminal, then retry.\n' >&2
  exit 1
fi
if [[ $found_project != "$project_id" ]]; then
  printf 'Project lookup did not return the requested project.\n' >&2
  exit 1
fi
printf 'CLI project access: OK (%s)\n' "$project_id"

if ! billing_enabled=$(gcloud billing projects describe "$project_id" --project="$project_id" --format='value(billingEnabled)' 2>/dev/null); then
  printf 'Cannot read billing status for project %s.\n' "$project_id" >&2
  exit 1
fi
case $billing_enabled in
  True|true) printf 'Billing status: visible (enabled)\n' ;;
  False|false) printf 'Billing status: visible (disabled)\n' ;;
  *) printf 'Billing status response was not recognized.\n' >&2; exit 1 ;;
esac

# Capture only long enough to ensure a nonempty token. Never display or save it.
if ! adc_token=$(gcloud auth application-default print-access-token 2>/dev/null); then
  printf 'ADC could not obtain an access token.\n' >&2
  printf 'Renew ADC interactively with: gcloud auth application-default login --project=%s --billing-project=%s\n' "$project_id" "$project_id" >&2
  exit 1
fi
if [[ -z $adc_token ]]; then
  printf 'ADC returned an empty access token.\n' >&2
  printf 'Renew ADC interactively with: gcloud auth application-default login --project=%s --billing-project=%s\n' "$project_id" "$project_id" >&2
  exit 1
fi
unset adc_token
printf 'ADC token acquisition: OK\n'
