# Cloud Landscape Report: AWS vs Azure

## Overview and Project Constraints

Project Nimbus evaluates AWS and Azure as the primary cloud platform for a mid-size SaaS product with a .NET API tier and Python data pipelines. The core requirement is evidence-based decision-making using the latest service direction for each provider, with special focus on AI/ML, data, and security offerings. The key open question is which service categories each provider is investing in most right now. Official AWS and Azure blogs are the primary evidence source.

**Limitations:**
- Per Azure’s robots.txt, agent-based access to https://azure.microsoft.com/en-us/blog/feed/ is barred. Automated comparison is only possible for AWS. Manual evidence for Azure can be incorporated if supplied later.

## Latest 10 AWS News Blog Posts by Service Category

| Rank | Provider | Title | Article URL | Primary Category |
|------|----------|-------|-------------|-----------------|
| 1 | AWS | AWS Lambda now supports GPU instances for Event Functions on Lambda Managed Instances | https://aws.amazon.com/blogs/aws/aws-lambda-now-supports-gpu-instances-for-event-functions-on-lambda-managed-instances/ | AI/ML, Compute |
| 2 | AWS | Four Continents, Four New AWS Heroes: Closing Out 2026 | https://aws.amazon.com/blogs/aws/four-continents-four-new-aws-heroes-closing-out-2026/ | Community, DevTools |
| 3 | AWS | AWS Weekly Roundup: AWS Nitro Sandboxes, AWS Emulator, and more (November 16, 2026) | https://aws.amazon.com/blogs/aws/aws-weekly-roundup-aws-nitro-sandboxes-aws-emulator-and-more-november-16-2026/ | Security, Compute, DevTools |
| 4 | AWS | Test your applications against AWS locally with AWS Emulator | https://aws.amazon.com/blogs/aws/test-your-applications-against-aws-locally-with-aws-emulator/ | DevTools |
| 5 | AWS | AWS Weekly Roundup: AgentCore Runtime V2, Amazon DynamoDB bulk put items, and more (November 9, 2026) | https://aws.amazon.com/blogs/aws/aws-weekly-roundup-agentcore-runtime-v2-amazon-dynamodb-bulk-put-items-and-more-november-9-2026/ | AI/ML, Data, DevTools |
| 6 | AWS | Amazon S3 Tables now offer managed migration of Apache Hive tables to Apache Iceberg | https://aws.amazon.com/blogs/aws/amazon-s3-tables-now-offer-managed-migration-of-apache-hive-tables-to-apache-iceberg/ | Data, Analytics |
| 7 | AWS | AWS Weekly Roundup: GPT-6.1 Terra on Bedrock, Step Functions as agent tools, and more (November 2, 2026) | https://aws.amazon.com/blogs/aws/aws-weekly-roundup-gpt-6-1-terra-on-bedrock-step-functions-as-agent-tools-and-more-november-2-2026/ | AI/ML, DevTools, Compute |
| 8 | AWS | How Nubank automated disaster recovery with the AWS DevOps Agent | https://aws.amazon.com/blogs/mt/how-nubank-automated-disaster-recovery-with-the-aws-devops-agent/ | Security, DevOps |
| 9 | AWS | How MoEngage turned over 400 APIs into agent tools with AgentCore Gateway | https://aws.amazon.com/blogs/machine-learning/how-moengage-turned-over-400-apis-into-agent-tools-with-agentcore-gateway/ | AI/ML, DevTools |
| 10 | AWS | Serverless ICYMI Q3 2026 | https://aws.amazon.com/blogs/compute/serverless-icymi-q3-2026/ | Compute, Serverless |

## Observations
- AWS investments remain strong in AI/ML, serverless compute, infrastructure automation, and emerging developer tooling such as emulation and agent integration.
- Data modernization (e.g., managed Iceberg tables, bulk ingest for DynamoDB) and robust hybrid/migration tooling are prominent.
- Security, compliance, and observability features receive ongoing attention (Nitro Sandboxes, DevOps automation for DR).
- AWS’s communication frames launches around operational simplicity, budget optimization, and extension of existing DevOps and serverless patterns.

## Limitations and Gaps
- No automated Azure evidence included due to provider restrictions. No claims are made about Azure’s recent launches or orientation.
- No numerical totals by category are supplied, as only AWS posts are available.

## Hypotheses and Recommendations
- AWS’s current momentum and service expansion center on: AI/ML infrastructure, data platform modernization, developer self-service, and secure compute.
- If Azure offers a comparable or greater concentration of innovation in these areas, a manual Azure post scan will be required for due diligence. If not, AWS sets the direction in these high-impact service domains for the period under review.

__Manual retrieval of Azure Blog evidence is needed to complete a strict AWS-vs-Azure service investment analysis._