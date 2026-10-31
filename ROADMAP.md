# Professional Cloud Architect study roadmap

- **Exam:** standard exam, January 14, 2027
- **Curriculum baseline:** [Google's v6.1 English exam guide](https://services.google.com/fh/files/misc/v6.1_pca_professional_cloud_architect_exam_guide_english.pdf)

This is a checklist for architecture knowledge and decision-making, not a Terraform course. Use Terraform only to support a lab when hands-on evidence is useful. For each topic, mark it complete when you can explain a suitable design, its trade-offs, and why plausible alternatives are less suitable for a given requirement. Link notes or lab evidence beside the checkbox as you go.

## Start here

Do one objective at a time. Spend about 60 minutes on each study session:

1. **10 minutes:** Read one unchecked objective below and write down what you already know, plus one question you cannot answer.
2. **20 minutes:** Read the relevant Google Cloud documentation or guide material to answer that question. Focus on when to choose a service, its limits, and its cost or operational trade-offs.
3. **20 minutes:** Apply it to a small scenario. Write the requirements, your choice, one alternative, and why the choice fits better.
4. **10 minutes:** Explain the decision without notes. Record anything you could not explain and start the next session there.

Start with **1.1 Business requirements**. Pick a system you know, such as a web application. Write three business goals and three technical constraints, then identify which decisions an architect needs to make. This needs no Terraform or GCP deployment. Keep the answer to one page; mark the checkbox only when you can explain it aloud.

At the end of each week, revisit the decisions you got wrong or guessed. Use a lab only when seeing a service run would answer a specific question. A short architecture decision and a clear explanation count as study progress.

## Target dates

| Dates | Focus | Exit evidence |
| --- | --- | --- |
| Oct 29–Nov 1 | Baseline, guide comparison, study setup | List changed live-guide objectives and choose the first weak areas. |
| Nov 2–8 | Section 1: business and technical architecture | Explain one architecture against business requirements and Well-Architected pillars. |
| Nov 9–15 | Section 1: network, compute, storage, data, migration | Draw a design and defend product choices and migration order. |
| Nov 16–22 | Section 2: network, storage, compute provisioning | Compare deployment and connectivity options; complete one small design or lab. |
| Nov 23–29 | Section 2: Vertex AI and AI product choices | Choose an ML/AI workflow and explain model, data, safety, and cost decisions. |
| Nov 30–Dec 6 | Section 3: security | Produce a least-privilege and data-protection design. |
| Dec 7–13 | Section 3 compliance; Section 4 processes | Explain audit, data residency, change, recovery, and cost decisions. |
| Dec 14–20 | Sections 5 and 6: implementation and operations | Produce a rollout, observability, support, and reliability plan. |
| Dec 21–27 | Case studies: Altostrat and Cymbal | Complete two one-page architecture briefs and review missed questions. |
| Dec 28–Jan 3 | Case studies: EHR and KnightMotives | Complete two more briefs and revisit weak objectives. |
| Jan 4–10 | Timed practice and guide recheck | Two timed sets, an error log, and an updated guide comparison. |
| Jan 11–13 | Final review | Revisit only unresolved decisions, case-study constraints, and exam logistics. |
| Jan 14 | Exam | Professional Cloud Architect standard exam. |

## 1. Design and plan a cloud solution architecture (~25%)

- [ ] **1.1 Business requirements:** distinguish functional and non-functional needs; map business goals, integration and data movement, security, observability, continuity, and cost to design decisions.
- [ ] **1.1 Success measures:** define KPIs, ROI, and trade-offs; decide whether to build, buy, modify, or deprecate a workload.
- [ ] **1.2 Technical requirements:** apply all six Well-Architected pillars; choose availability, failover, scaling, performance, latency, backup, and recovery targets.
- [ ] **1.3 Network and hybrid design:** compare VPC, peering, routing, firewalls, load balancing, Shared VPC, Private Service Connect, and on-premises or multicloud connectivity.
- [ ] **1.3 Compute and data choices:** choose among Compute Engine, GKE, Cloud Run, Cloud Run functions, Spot VMs, storage types, databases, and data processing options for a scenario.
- [ ] **1.3 AI choices:** identify where Gemini models, Agent Builder, Model Garden, or AI Hypercomputer fit, including when a simpler solution is enough.
- [ ] **1.4 Migration:** document dependencies, workload and data migration sequence, testing, network changes, license effects, and financial impact.
- [ ] **1.5 Evolution:** propose future improvements as business needs and Google Cloud capabilities change.

## 2. Manage and provision solution infrastructure (~18%)

- [ ] **2.1 Network topologies:** design secure hybrid and multicloud paths, VPC boundaries, firewall policy, and load-balancer access.
- [ ] **2.2 Storage systems:** choose capacity, access, retention and lifecycle, latency, growth, backup, recovery, and data protection settings.
- [ ] **2.3 Compute systems:** compare standard and Spot VMs, GKE, serverless, and VMware Engine; explain networking, orchestration, patching, and configuration management.
- [ ] **2.4 Vertex AI workflows:** explain Pipelines, data integration, and the ML lifecycle; choose GPU, TPU, or other AI Hypercomputer options by workload and cost.
- [ ] **2.5 Prebuilt AI:** distinguish relevant Google AI APIs, Gemini Enterprise features, NotebookLM, and Model Garden models for a business request.

## 3. Design for security and compliance (~19%)

- [ ] **3.1 Identity and hierarchy:** design organization, folder, and project boundaries; IAM roles, service account access, separation of duties, and impersonation.
- [ ] **3.1 Data controls:** choose encryption and key ownership, Cloud KMS, secret management, and audit logging.
- [ ] **3.1 Perimeter and access:** explain organization policy, hierarchical firewall policy, VPC Service Controls, context-aware access, IAP, and Workload Identity Federation.
- [ ] **3.1 Supply chain and AI:** address software supply chain security, Model Armor, Sensitive Data Protection, and secure model deployment.
- [ ] **3.2 Compliance:** map privacy, sovereignty, regulated data, industry certifications, and audit requirements to architecture controls and evidence.

## 4. Analyze and optimize technical and business processes (~15%)

- [ ] **4.1 Technical processes:** compare SDLC and CI/CD approaches; define testing, validation, incident root-cause analysis, service provisioning, and disaster recovery.
- [ ] **4.2 Business processes:** account for stakeholders, change management, team readiness, decision ownership, customer success, and CapEx/OpEx trade-offs.
- [ ] **4.3 Production reliability:** define safe chaos, penetration, and recovery exercises, with success criteria and rollback.

## 5. Manage implementation (~11%)

- [ ] **5.1 Delivery advice:** plan application and infrastructure rollout, unit/integration/load tests, migration tooling, API management with Apigee, and Gemini Cloud Assist use.
- [ ] **5.2 Programmatic access:** know when to use Cloud Shell, Cloud Code, `gcloud`, `gsutil`, `bq`, emulators, client libraries, Google APIs, and IaC.
- [ ] **5.2 Terraform boundary:** read a plan and explain its architecture and risk; keep Terraform syntax and module design as implementation tools rather than exam goals.

## 6. Ensure solution and operations excellence (~12%)

- [ ] **6.1 Operational excellence:** apply the Well-Architected operational excellence recommendations to ownership, change, and incident response.
- [ ] **6.2 Observability:** choose logs, metrics, traces or profiling, benchmarks, alert thresholds, and actionable notifications.
- [ ] **6.3–6.5 Delivery and support:** explain release management, support paths, quality controls, and how to improve them from operational evidence.
- [ ] **6.6 Reliability:** design load, chaos, and penetration tests with explicit safety boundaries and recovery checks.

## Case studies

For each case, create a one-page brief: business and technical constraints, proposed architecture, two rejected alternatives, security and compliance, reliability, cost, and a short explanation of why the design meets the stated goals. The four links below are the case studies named in the v6.1 guide.



- [ ] [Altostrat Media](https://services.google.com/fh/files/misc/v6.1_pca_altostrat_media_case_study_english.pdf): media workflows, hybrid ingestion, GenAI, storage cost, and reliability.
- [ ] [Cymbal Retail](https://services.google.com/fh/files/misc/v6.1_pca_cymbal_retail_case_study_english.pdf): catalog enrichment, conversational discovery, legacy integrations, and human review.
- [ ] [EHR Healthcare](https://services.google.com/fh/files/misc/v6.1_pca_ehr_healthcare_case_study_english.pdf): hybrid migration, regulated data, container platforms, and availability.
- [ ] [KnightMotives Automotive](https://services.google.com/fh/files/misc/v6.1_pca_knightmotives_automotive_case_study_english.pdf): connected vehicles, legacy modernization, AI data, connectivity, and EU privacy.

## Practice and readiness

- [ ] Compare the current live standard guide with v6.1 now; record changes to objectives, weights, product names, and case studies.
- [ ] Complete Google's [sample questions](https://cloud.google.com/learn/certification/cloud-architect/) and keep an error log: missed requirement, better choice, and the reason.
- [ ] Complete two timed, two-hour practice sets and revisit every answer that was guessed or missed.
- [ ] Revisit the live guide during Jan 4–10 and update this checklist for any standard-exam changes.
- [ ] Explain the four case studies and the major product trade-offs without notes.
- [ ] Confirm exam appointment, delivery method, and ID requirements before Jan 14.

Hands-on labs are optional evidence for these objectives. Before any deployment, confirm billing guardrails and follow [AGENTS.md](AGENTS.md) for reviewed plans, explicit `apply` or `destroy` approval, and post-destroy resource checks.
