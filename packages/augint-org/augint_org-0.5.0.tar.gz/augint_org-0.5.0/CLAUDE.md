# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AWS Control Tower landing zone implementation using direct StackSets (no CfCT complexity) for automated multi-account provisioning. New accounts receive resources automatically based on their OU placement - Production gets everything (pipelines, monitoring, backups, logging), Staging gets essentials, Sandbox gets nothing.

## Architecture

- **Control Tower Foundation**: Management account hosts Control Tower which manages Audit and Log Archive accounts
- **OU Hierarchy**:
  ```
  Root
  ├── Security (CT managed)
  ├── Sandbox (unrestricted, no StackSets)
  └── Workloads (SCPs applied)
      ├── Production (all StackSets + backups + logging)
      └── Staging (pipeline StackSets only)
  ```
- **Direct StackSets**: Automated configurations with auto-deployment based on OU placement

## Key Commands

### Docker-based Development
```bash
make claude           # Launch Claude Code in Docker container
make claude-x         # Launch with skip permissions flag
make join-claude      # Open bash in Claude container
make docker-build     # Build containers
make docker-stop      # Stop containers
```

### StackSet Deployment
```bash
python -m scripts.deploy  # Deploy all StackSets and SCPs
```

## Project Structure

### StackSet Templates (`stacksets/`)
- **01-pipeline-bootstrap/**: S3 bucket and CloudFormation execution role
- **02-github-oidc/**: GitHub Actions OIDC provider and SAMDeployRole
- **03-monitoring/**: CloudWatch alarms for serverless workloads
- **04-cost-management/**: Budget alerts and cost anomaly detection
- **05-account-notifications/**: Email notifications for new account creation
- **06-log-aggregation/**: Centralized logging to Log Archive (Production only)
- **07-backup-strategy/**: AWS Backup configuration (Production only)
- **scps/**: Service Control Policies for Workloads OU

### Key Design Patterns

1. **Account Strategy**: Two accounts per product (staging/prod), e.g., `lls-staging` and `lls-prod`
2. **OU-based Deployment**: Production gets full suite, Staging gets essentials, Sandbox gets nothing
3. **OIDC Authentication**: GitHub Actions assume `SAMDeployRole` via OIDC (no IAM users/keys)
4. **DNS Pattern**: Production owns apex domain, staging owns subdomain
5. **Auto-deployment**: New accounts automatically receive StackSets based on OU placement

## Environment Variables

Required for deployment scripts:
- `GITHUB_ORG`: GitHub organization (default: svange)
- `GITHUB_REPO`: Repository name (default: aillc-org)
- `NOTIFICATIONS_EMAIL`: Email for all alerts and notifications
- `BUDGETS_MONTHLY_DEFAULT`: Monthly budget in USD (default: 1000)
- `BUDGETS_ANOMALY_THRESHOLD`: Anomaly alert threshold (default: 100)

## Important Constraints

- **No IAM Users**: Enforced by SCP - only SSO users and OIDC roles permitted
- **Control Tower Ownership**: Do not reimplement features Control Tower manages (CloudTrail, Config, guardrails)
- **Manual Steps Required**: Initial SSO user creation and Control Tower setup are console operations
- **Region Restrictions**: SCPs enforce region allow-list for workload accounts

## Testing & Validation

After deployment, verify:
1. SCPs attached to Workloads OU (inherited by Production/Staging)
2. StackSet instances created in appropriate accounts
3. Production accounts have backups and log aggregation
4. Staging accounts have pipeline resources but no backups
5. New account creation triggers email notification
