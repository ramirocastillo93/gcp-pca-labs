# Google Cloud Professional Cloud Architect labs

This repository supports preparation for the **Professional Cloud Architect standard exam on January 14, 2027**. The curriculum baseline is [Google's v6.1 standard exam guide](https://services.google.com/fh/files/misc/v6.1_pca_professional_cloud_architect_exam_guide_english.pdf). The PDF stays outside this repository.

Track the exam objectives, case studies, and target dates in [ROADMAP.md](ROADMAP.md).

The [live certification page](https://cloud.google.com/learn/certification/cloud-architect/) and its standard exam guide can change. Before the exam, compare the then-current standard guide with v6.1, record any changed objectives or case studies in a study note, and adjust the remaining labs accordingly.

## Study approach

Labs will test architecture choices against the guide's objectives. Each lab should record the scenario and requirements, a diagram or resource inventory, the chosen design and alternatives, security and reliability implications, cost assumptions, evidence from the exercise, and cleanup results. Study notes and lab directories will be added when their first contents are ready.

Terraform may be drafted with AI assistance to provision lab resources. Terraform itself is a tool for the exercises, not a study objective. Every future deployment must follow [AGENTS.md](AGENTS.md), including explicit approval for each `apply` and `destroy`.

## Local access check

Install the [Google Cloud CLI](https://cloud.google.com/sdk/docs/install), authenticate the CLI for the lab project, and set up [Application Default Credentials (ADC)](https://docs.cloud.google.com/docs/authentication/application-default-credentials) for local tooling. CLI credentials and ADC are separate; a working `gcloud` login does not establish that ADC works. Keep credential files outside this repository.

Copy the template and set `GCP_PROJECT_ID` to the **lab project ID you intend to use**. The `.env` file is ignored by Git; `.env.example` contains no real project ID or secrets. Use plain `KEY=value` syntax without quotes.

```sh
cp .env.example .env
# Edit .env and set GCP_PROJECT_ID to your lab project ID.
./scripts/check-access.sh
```

The script requires a valid project ID in `.env` and rejects `nakamalabsio`. It checks CLI access to that project, whether its billing status is visible, and whether ADC can obtain a token. It suppresses the token and does not change the active `gcloud` configuration or create GCP resources. An ADC success only establishes that a token can be obtained; it does not prove that ADC has permission on the lab project. A visible billing status is not confirmation that budgets or other billing guardrails are in place. Confirm those guardrails before the first deployment.

Run the script as `./scripts/check-access.sh` or `bash scripts/check-access.sh`; it uses Bash. If the CLI project check fails, run `gcloud projects describe YOUR_LAB_PROJECT_ID --project=YOUR_LAB_PROJECT_ID` to see the underlying error. For an expired CLI login, renew it interactively with `gcloud auth login` and retry the script. If ADC fails, run `gcloud auth application-default login --project=YOUR_LAB_PROJECT_ID --billing-project=YOUR_LAB_PROJECT_ID` interactively, then retry. This replaces the previous local ADC login and explicitly selects the lab project for quota and billing; the ADC account needs permission to use it as a quota project.

## Terraform bootstrap

The root configuration is in `terraform/`. It pins the official `hashicorp/google` provider and takes its project ID from a required Terraform variable. Terraform reads the ignored `terraform/terraform.tfvars` file automatically when run from that directory. Set `project_id` there to the lab project ID, matching `.env`; the provider does not rely on the active `gcloud` project. The provider has no default region yet. Choose a region explicitly when a lab needs one.

```sh
# On a fresh clone, copy the template once:
cp -n terraform/terraform.tfvars.example terraform/terraform.tfvars
# Edit terraform/terraform.tfvars and set project_id to your lab project ID.
terraform -chdir=terraform init -backend=false
terraform -chdir=terraform fmt -check
terraform -chdir=terraform validate
terraform -chdir=terraform plan
```

Initialization only installs the provider locally and creates the provider lock file. Commit `terraform/.terraform.lock.hcl` when publishing the repository; keep `.terraform/`, `terraform/terraform.tfvars`, and local state ignored. The current root has no resources, modules, or remote backend. A plan should show no changes. Future `apply` and `destroy` runs require the separate approvals and checks in [AGENTS.md](AGENTS.md).

## Before any public push

Review the exact staged file list and diff with `git diff --cached --name-status` and `git diff --cached`. Check for credentials, secret values, Terraform state and plans, local variable files, and the source PDF. Ignore rules do not protect files already tracked by Git.
