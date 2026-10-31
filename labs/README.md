# Interview architecture labs (October 30–November 1)

These three labs prepare for the sports booking interview. They use small, inspectable open-source components instead of recreating the whole platform. The goal is to explain failure modes, migration choices, and evidence, not to finish a production system in three days.

| Day | Lab | Interview question to answer |
| --- | --- | --- |
| Friday | [01: database sync](01-database-sync/README.md) | How do we migrate data without conflicting writes or losing changes? |
| Saturday | [02: identity and payments](02-identity-payments/README.md) | How do retries, asynchronous webhooks, refunds, and notifications avoid duplicates? |
| Sunday | [03: analytics](03-analytics/README.md) | How do operational databases feed reporting without harming bookings? |

For the interview, draw one target architecture that connects the three labs. Give the **games service** sole authority over capacity and holds, and the **payments service** sole authority over payment commands and provider IDs. Keep webhook delivery and notification delivery asynchronous. The sync worker and analytics pipeline observe or move data; neither may create a second payment. A 10-minute hold requires an expiry rule and a clear response when a payment succeeds after expiry.

Labs 01 and 02 have standalone Terraform roots; Lab 03's Terraform is planned. The existing ignored `terraform/terraform.tfvars` supplies `project_id` through an explicit `-var-file` argument; it is never inferred from the active `gcloud` project. Lab resources can be billable. Review the plan, target project, billing guardrails, and [AGENTS.md](../AGENTS.md) before each separate apply or destroy.

Lab 01 has been provisioned for the database sync exercise. Labs 02 and 03 are planned. The labs deliberately avoid storing provider API keys or database passwords in Terraform variables or state. Any external sample repository should be cloned outside this repository and inspected before use. Record observations and answers in local notes; do not commit customer data, credentials, or payment identifiers.
