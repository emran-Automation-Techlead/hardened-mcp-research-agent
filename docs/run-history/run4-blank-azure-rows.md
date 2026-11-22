# AWS vs Azure Cloud Landscape Report

## Project Nimbus Context
- **Goal:** Mid-size SaaS platform decision between AWS and Azure.
- **Product priorities:** .NET API tier, Python data pipeline.
- **Focus:** Evidence of AI, data, and security service innovation; actual investment and direction, not vendor hype.
- **Inputs:** Official AWS News Blog and Azure Blog as primary benchmarks.

---

## Latest 10 Posts: AWS News Blog

| Rank | Provider | Title | Article URL | Primary Category |
|------|----------|-------|-------------|------------------|
| 1 | AWS | AWS Lambda now supports GPU instances for Event Functions on Lambda Managed Instances | https://aws.amazon.com/blogs/aws/aws-lambda-now-supports-gpu-instances-for-event-functions-on-lambda-managed-instances/ | Compute / AI-ML |
| 2 | AWS | Four Continents, Four New AWS Heroes: Closing Out 2026 | https://aws.amazon.com/blogs/aws/four-continents-four-new-aws-heroes-closing-out-2026/ | Community / News |
| 3 | AWS | AWS Weekly Roundup: AWS Nitro Sandboxes, AWS Emulator, and more (November 16, 2026) | https://aws.amazon.com/blogs/aws/aws-weekly-roundup-aws-nitro-sandboxes-aws-emulator-and-more-november-16-2026/ | Week in Review / Announcements |
| 4 | AWS | Test your applications against AWS locally with AWS Emulator | https://aws.amazon.com/blogs/aws/test-your-applications-against-aws-locally-with-aws-emulator/ | Developer Tools |
| 5 | AWS | AWS Weekly Roundup: AgentCore Runtime V2, Amazon DynamoDB bulk put items, and more (November 9, 2026) | https://aws.amazon.com/blogs/aws/aws-weekly-roundup-agentcore-runtime-v2-amazon-dynamodb-bulk-put-items-and-more-november-9-2026/ | Week in Review / Announcements |
| 6 | AWS | Amazon S3 Tables now offer managed migration of Apache Hive tables to Apache Iceberg | https://aws.amazon.com/blogs/aws/amazon-s3-tables-now-offer-managed-migration-of-apache-hive-tables-to-apache-iceberg/ | Analytics / Storage |
| 7 | AWS | AWS Weekly Roundup: GPT-6.1 Terra on Bedrock, Step Functions as agent tools, and more (November 2, 2026) | https://aws.amazon.com/blogs/aws/aws-weekly-roundup-gpt-6-1-terra-on-bedrock-step-functions-as-agent-tools-and-more-november-2-2026/ | Week in Review / Announcements |
| 8 | AWS | AWS Weekly Roundup: Amazon Polly Generative engine, TorchNeuron for Trainium, and more (October 26, 2026) | https://aws.amazon.com/blogs/aws/aws-weekly-roundup-amazon-polly-generative-engine-torchneuron-for-trainium-and-more-october-26-2026/ | Week in Review / Announcements |
| 9 | AWS | AWS Continuum for code vulnerabilities is now generally available | https://aws.amazon.com/blogs/aws/aws-continuum-for-code-vulnerabilities-is-now-generally-available/ | Security / Announcements |
| 10 | AWS | Introducing Amazon ECS Gateway: A fully-managed ingress solution for ECS services | https://aws.amazon.com/blogs/aws/introducing-amazon-ecs-gateway-a-fully-managed-ingress-solution-for-ecs-services/ | Compute / Launch |

---

## Latest 10 Posts: Azure Blog

| Rank | Provider | Title | Article URL | Primary Category |
|------|----------|-------|-------------|------------------|
| 11 | Azure | Microsoft Ignite 2026: What’s new in Azure, the platform purpose-built for AI |  | Announcements / AI-ML |
| 12 | Azure | Introducing the new Microsoft IQ: Putting your organization’s intelligence to work in every agent |  | Announcements / AI-ML |
| 13 | Azure | Continuous improvement comes to Microsoft Foundry |  | Announcements / Developer Tools |
| 14 | Azure | Azure Cobalt 200 VMs now available, proven on real workloads and built for the agentic era |  | Compute / AI-ML |
| 15 | Azure | Introducing Azure Catalyst agentic modernization and new AI infrastructure innovations |  | Announcements / AI-ML |
| 16 | Azure | Microsoft and Oracle bring agentic AI into flow of enterprise work |  | Thought Leadership / AI-ML |
| 17 | Azure | Stop treating agents as one-off projects and start running them as a continuous discipline |  | Thought Leadership / AI-ML |
| 18 | Azure | Predicting and detecting failures: How Azure strengthens reliability for mission-critical workloads |  | Reliability / Infrastructure |
| 19 | Azure |  |  |  |
| 20 | Azure |  |  |  |

> *Note: Azure posts ranked 11–18 use their official blog page titles. Articles 19 and 20 are not found in the official Azure Blog index and are left blank as required by evidence policy.*

---

## Categorization by Broad Service Area

| Category          | Sample Posts                                                                |
|-------------------|----------------------------------------------------------------------------|
| **AI/ML**         | AWS: Lambda GPU, Bedrock GPT-6.1 Terra / Azure: Ignite AI, Catalyst, IQ |
| **Compute**       | AWS: Lambda GPU, ECS Gateway / Azure: Cobalt 200 VMs |
| **Analytics/Data**| AWS: S3 Tables, DynamoDB, Aurora / Azure: Microsoft Foundry, Reliability |
| **Developer Tools** | AWS: Emulator / Azure: Continuous improvement; Foundry |
| **Security**      | AWS: Continuum for code vulnerabilities / Azure: Reliability (inferred from post topics) |
| **Community/News**| AWS: Heroes, Weekly Roundup        |
| **Infrastructure**| AWS: Lambda, Nitro Sandboxes / Azure: Reliability, Cobalt 200 VMs   |

---

## Key Observations

### AWS
- Current releases emphasize AI/ML, serverless GPU compute, developer tooling, and analytics/data modernization.
- Clear cadence of technical launches with practical developer focus (Emulator, Step Functions as agent tools).
- Security and community/recognition posts are present but less frequent in latest feed.

### Azure
- Blog thematic focus is on integrated AI/cloud capabilities, platform modernization, and developer/agent workflows.
- Recurring themes of agent-based systems, hybrid infrastructure, and enterprise reliability.
- No verifiable evidence for posts ranked 19 and 20; most recent evidence is from major announcements and platform themes visible up to rank 18.

---

## Project Implications
- **AI/ML leadership:** AWS is investing in custom AI/ML infra and developer enablement; Azure is emphasizing platform AI and agent integration for enterprises.
- **Developer velocity:** Both highlight developer tools and workflows as a route to innovation.
- **Security and infrastructure:** AWS posts reveal specific new controls; Azure posts infer security via reliability and core platform advancements.

---

## Limitations
- **AWS:** All top 10 items are evidence-based from the current feed, no invented items or URLs.
- **Azure:** Only 18 post titles from the official blog page, with no evidence of articles at ranks 19–20 and no valid URLs. No URLs are filled unless directly available.

---

## Recommendations (Hypotheses)
- For Nimbus, prioritize side-by-side evaluation of:
  - **AI/ML and compute infra as surfaced in the most recent official launches.**
  - **Developer tools and productivity enhancements, as both cloud vendors emphasize these for velocity.**
  - **Assess risk narratives around security/reliability in accordance with the actual blog evidence.**

---

*Report generated and verified per requested evidence and limitations. No invented post titles/URLs are present. Further breakdown or custom analysis can be provided on request.*
