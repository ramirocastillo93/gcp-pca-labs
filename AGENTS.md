# Agent instructions

This repository is for Professional Cloud Architect exam study. AI may draft Terraform and review architecture decisions, but a human owner controls cloud changes.

- Require an explicit lab project ID for every cloud operation. Never fall back to the active `gcloud` project or use `nakamalabsio` as a lab target.
- Before any `terraform apply`, present the plan for review, confirm the target project, and confirm billing guardrails. Obtain the owner's explicit approval for **each** apply.
- Before any `terraform destroy`, present the target and destruction plan for review and obtain the owner's explicit approval for **each** destroy. Afterward, check for remaining lab resources and document the result.
- Do not make unattended cloud changes, including resource creation, updates, deletion, API enablement, or billing changes.
- Never commit credential files, secret values, Terraform state, plans, or local variable files. Never print or persist secret values in logs or repository files.
- Before a public push, review the staged file list and diff. `.gitignore` does not protect files already tracked by Git.
