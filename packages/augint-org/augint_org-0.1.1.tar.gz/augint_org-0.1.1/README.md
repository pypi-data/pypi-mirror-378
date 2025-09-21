# aillc-org — Control Tower + Direct StackSets Landing Zone 🚀

**Enterprise-ready AWS Organization management with automated account provisioning, Control Tower integration, and comprehensive CI/CD.**

Automated AWS multi-account landing zone. Set it up once, never touch it again. New accounts auto-provision based on their OU placement.

[![Library Publishing](https://github.com/svange/aillc-org/actions/workflows/publish.yaml/badge.svg?branch=main)](https://github.com/svange/aillc-org/actions/workflows/publish.yaml)
[![Infrastructure](https://github.com/svange/aillc-org/actions/workflows/infrastructure.yaml/badge.svg?branch=main)](https://github.com/svange/aillc-org/actions/workflows/infrastructure.yaml)
[![PyPI](https://img.shields.io/pypi/v/augint-org?style=flat-square)](https://pypi.org/project/augint-org/)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg?style=flat-square)](https://www.python.org/downloads/)

[![uv](https://img.shields.io/badge/dependency%20manager-uv-blue?style=flat-square)](https://github.com/astral-sh/uv)
[![Linting: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json&style=flat-square)](https://github.com/astral-sh/ruff)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?style=flat-square&logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![Type Checked: mypy](https://img.shields.io/badge/type--checked-mypy-blue?style=flat-square)](http://mypy-lang.org/)

[![pytest](https://img.shields.io/badge/testing-pytest-green?style=flat-square&logo=pytest)](https://pytest.org/)
[![GitHub Actions](https://img.shields.io/badge/CI-GitHub%20Actions-blue?style=flat-square&logo=github-actions)](https://github.com/features/actions)
[![Semantic Release](https://img.shields.io/badge/release-semantic--release-e10079?style=flat-square&logo=semantic-release)](https://github.com/semantic-release/semantic-release)
[![AWS Control Tower](https://img.shields.io/badge/AWS-Control%20Tower-orange?style=flat-square&logo=amazon-aws)](https://aws.amazon.com/controltower/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [Getting Started](docs/getting-started.md) | Quick setup guide and first steps |
| [Configuration](docs/configuration.md) | Environment variables and settings |
| [Architecture](docs/architecture.md) | System design and components |
| [Development](docs/development.md) | Development setup and guidelines |
| [API Reference](https://svange.github.io/aillc-org) | Auto-generated API documentation |

## 📊 Live Dashboards

| 📖 **[Documentation](https://svange.github.io/aillc-org)** | 🧪 **[Unit Tests](https://svange.github.io/aillc-org/unit-test-report.html)** | 🔬 **[Integration Tests](https://svange.github.io/aillc-org/integration-test-report.html)** | 📊 **[Coverage](https://svange.github.io/aillc-org/htmlcov/index.html)** | 🔒 **[Security](https://svange.github.io/aillc-org/security-reports.html)** | ⚖️ **[Compliance](https://svange.github.io/aillc-org/license-compatibility.html)** |
|:-:|:-:|:-:|:-:|:-:|:-:|

## 🔑 Key Development Characteristics

| Characteristic | Details |
|:--------------|:--------|
| **Package Manager** | uv (10-100x faster than pip/poetry) |
| **Deployment Model** | Tag-based releases to PyPI |
| **Infrastructure** | AWS StackSets + Service Control Policies |
| **Environments** | Dev → Staging → Production |
| **Pipeline Features** | Conditional deployments, Semantic release, Auto-publish |
| **Quality Gates** | 80% coverage, Type checking, Security scanning |
| **Special Features** | Control Tower integration, Auto-account provisioning |

---

## 🚀 Quick Start (2 minutes)

```bash
# Prerequisites: Control Tower active, AWS SSO configured
aws sso login --profile org

# Option 1: One command setup (includes GitHub Actions role)
make quickstart

# Option 2: Step by step
make bootstrap  # Create OUs and enable Control Tower baselines (idempotent)
make setup      # Create GitHub Actions role (shows ARN for GitHub secrets)
make deploy     # Deploy everything
make status     # Verify deployment
```

**📌 Note about Control Tower Baselines**: The bootstrap command now automatically enables Control Tower baselines for all OUs under Workloads. This allows Account Factory to place accounts directly into Production/Staging OUs. This process takes ~2-3 minutes per OU.

**📌 IMPORTANT**: The first run creates a GitHub Actions role (OrgPipelineRole).
- Copy the ARN from `make setup` output
- Add to GitHub: `gh secret set AWS_ROLE_ARN --body 'arn:...'`
- This enables automated deployments via GitHub Actions

**That's it!** New accounts will auto-provision. Place them in:
- **Production OU**: Gets everything (pipelines, backups, monitoring, logging)
- **Staging OU**: Gets essentials (pipelines, basic monitoring)
- **Sandbox OU**: Gets nothing (unrestricted)

---

## TL;DR — What happens automatically

**Production Account Creation:**
1. Place in Workloads/Production OU
2. Gets **everything**: Pipeline resources, monitoring, backups, log aggregation
3. Email notification with .env-ready configuration

**Staging Account Creation:**
1. Place in Workloads/Staging OU
2. Gets **essentials**: Pipeline resources, basic monitoring
3. No backups or log aggregation (cost savings)

**Sandbox Account Creation:**
1. Place in Sandbox OU
2. Gets **nothing**: Complete freedom, no restrictions

**Within ~5 minutes, accounts are ready for `sam deploy`**

---

## Architecture (Simple + Automated)

- **Control Tower manages**: Security OU, Sandbox OU, Log Archive, Audit, CloudTrail, Config, SSO
- **You manage**: Workloads OU with Production/Staging nested underneath
- **StackSets auto-deploy** based on OU placement:
  - Workloads level: Pipeline resources, monitoring, cost management
  - Production only: Backup vaults, log aggregation
  - Management only: Account creation notifications
- **Per product**: Two accounts (`product-staging`, `product-prod`)
- **DNS pattern**: Prod owns apex (`example.com`), staging owns subdomain (`staging.example.com`)

---

## Prerequisites

✅ **Before you start**, ensure:
- AWS Control Tower is activated
- You have Management account access via SSO
- AWS CLI v2 installed with SSO configured
- Python 3.9+ installed
- `.env` file created with `NOTIFICATIONS_EMAIL=your-email@example.com`

---

## How It Works

The `make quickstart` command:
1. Creates the OU structure (Workloads → Production/Staging)
2. Deploys 7 StackSets with auto-deployment enabled
3. Attaches SCPs to Workloads OU
4. Sets up email notifications for new accounts

After this, **every new account automatically gets resources** based on its OU:

| Resource | Production | Staging | Sandbox |
|----------|------------|---------|----------|
| S3 Pipeline Bucket | ✅ | ✅ | ❌ |
| GitHub OIDC Roles | ✅ | ✅ | ❌ |
| CloudWatch Monitoring | ✅ | ✅ | ❌ |
| Budget Alerts | ✅ | ✅ | ❌ |
| Automated Backups | ✅ | ❌ | ❌ |
| Centralized Logging | ✅ | ❌ | ❌ |
| Security Policies | ✅ | ✅ | ❌ |

---

## Manual Deployment (Advanced)

If you prefer to understand each step or need to customize:

### Step 1: Create OU Structure

```bash
# Create parent Workloads OU
WORKLOADS_OU=$(aws organizations create-organizational-unit \
  --parent-id $(aws organizations list-roots --query 'Roots[0].Id' --output text --profile org) \
  --name Workloads \
  --query 'OrganizationalUnit.Id' \
  --output text \
  --profile org)

# Create Production OU under Workloads
PROD_OU=$(aws organizations create-organizational-unit \
  --parent-id $WORKLOADS_OU \
  --name Production \
  --query 'OrganizationalUnit.Id' \
  --output text \
  --profile org)

# Create Staging OU under Workloads
STAGING_OU=$(aws organizations create-organizational-unit \
  --parent-id $WORKLOADS_OU \
  --name Staging \
  --query 'OrganizationalUnit.Id' \
  --output text \
  --profile org)

echo "Workloads OU: $WORKLOADS_OU"
echo "Production OU: $PROD_OU"
echo "Staging OU: $STAGING_OU"
```

---

### Step 2: Deploy Management Account Resources

### Account Notifications (Management Account Only)
```bash
# Deploy notification system for new account creation
aws cloudformation create-stack-set \
  --stack-set-name account-notifications \
  --template-body file://stacksets/05-account-notifications/template.yaml \
  --parameters ParameterKey=NotificationEmail,ParameterValue=your-email@example.com \
  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
  --profile org

# Deploy to Management account only
aws cloudformation create-stack-instances \
  --stack-set-name account-notifications \
  --accounts $(aws sts get-caller-identity --query 'Account' --output text --profile org) \
  --regions us-east-1 \
  --profile org
```

### Step 3: Deploy StackSets to Workloads OU

### A) Pipeline Bootstrap Resources
```bash
# Create the StackSet with auto-deployment enabled
aws cloudformation create-stack-set \
  --stack-set-name pipeline-bootstrap \
  --template-body file://stacksets/01-pipeline-bootstrap/template.yaml \
  --capabilities CAPABILITY_NAMED_IAM \
  --auto-deployment Enabled=true,RetainStacksOnAccountRemoval=false \
  --profile org

# Deploy to Workloads OU (auto-deploys to both Production and Staging!)
aws cloudformation create-stack-instances \
  --stack-set-name pipeline-bootstrap \
  --deployment-targets OrganizationalUnitIds=$WORKLOADS_OU \
  --regions us-east-1 \
  --profile org
```

### B) GitHub OIDC + Deploy Role
```bash
# Create StackSet
aws cloudformation create-stack-set \
  --stack-set-name github-oidc \
  --template-body file://stacksets/02-github-oidc/template.yaml \
  --parameters ParameterKey=GitHubOrg,ParameterValue=svange \
  --capabilities CAPABILITY_NAMED_IAM \
  --auto-deployment Enabled=true,RetainStacksOnAccountRemoval=false \
  --profile org

# Deploy to Workloads OU
aws cloudformation create-stack-instances \
  --stack-set-name github-oidc \
  --deployment-targets OrganizationalUnitIds=$WORKLOADS_OU \
  --regions us-east-1 \
  --profile org
```

### C) Monitoring
```bash
# Create StackSet
aws cloudformation create-stack-set \
  --stack-set-name monitoring-baseline \
  --template-body file://stacksets/03-monitoring/template.yaml \
  --parameters ParameterKey=AlarmEmail,ParameterValue=your-email@example.com \
  --capabilities CAPABILITY_NAMED_IAM \
  --auto-deployment Enabled=true,RetainStacksOnAccountRemoval=false \
  --profile org

# Deploy to Workloads OU
aws cloudformation create-stack-instances \
  --stack-set-name monitoring-baseline \
  --deployment-targets OrganizationalUnitIds=$WORKLOADS_OU \
  --regions us-east-1 \
  --profile org
```

### D) Cost Management
```bash
# Create StackSet
aws cloudformation create-stack-set \
  --stack-set-name cost-management \
  --template-body file://stacksets/04-cost-management/template.yaml \
  --parameters \
    ParameterKey=BudgetEmail,ParameterValue=your-email@example.com \
    ParameterKey=MonthlyBudget,ParameterValue=1000 \
  --capabilities CAPABILITY_NAMED_IAM \
  --auto-deployment Enabled=true,RetainStacksOnAccountRemoval=false \
  --profile org

# Deploy to Workloads OU
aws cloudformation create-stack-instances \
  --stack-set-name cost-management \
  --deployment-targets OrganizationalUnitIds=$WORKLOADS_OU \
  --regions us-east-1 \
  --profile org
```

### Step 4: Deploy Production-Only StackSets

### A) Log Aggregation
```bash
# Create StackSet
aws cloudformation create-stack-set \
  --stack-set-name log-aggregation \
  --template-body file://stacksets/06-log-aggregation/template.yaml \
  --parameters ParameterKey=LogArchiveAccountId,ParameterValue=405826043153 \
  --capabilities CAPABILITY_IAM \
  --auto-deployment Enabled=true,RetainStacksOnAccountRemoval=false \
  --profile org

# Deploy to Production OU only
aws cloudformation create-stack-instances \
  --stack-set-name log-aggregation \
  --deployment-targets OrganizationalUnitIds=$PROD_OU \
  --regions us-east-1 \
  --profile org
```

### B) Backup Strategy
```bash
# Create StackSet
aws cloudformation create-stack-set \
  --stack-set-name backup-strategy \
  --template-body file://stacksets/07-backup-strategy/template.yaml \
  --capabilities CAPABILITY_IAM CAPABILITY_NAMED_IAM \
  --auto-deployment Enabled=true,RetainStacksOnAccountRemoval=false \
  --profile org

# Deploy to Production OU only
aws cloudformation create-stack-instances \
  --stack-set-name backup-strategy \
  --deployment-targets OrganizationalUnitIds=$PROD_OU \
  --regions us-east-1 \
  --profile org
```

---

### Step 5: Apply Service Control Policies

```bash
# Create the SCP
aws organizations create-policy \
  --name workloads-baseline \
  --description "Baseline security for workload accounts" \
  --type SERVICE_CONTROL_POLICY \
  --content file://stacksets/scps/workloads-baseline.json \
  --profile org

# Attach to Workloads OU (inherited by Production and Staging)
aws organizations attach-policy \
  --policy-id p-xxxxxxxx \
  --target-id $WORKLOADS_OU \
  --profile org
```

---

### Step 6: Create Workload Accounts

Use Control Tower Account Factory (console) or CLI:

```bash
# Example: Create staging account for project
aws organizations create-account \
  --email project-staging@yourcompany.com \
  --account-name "project-staging" \
  --profile org

# Example: Create production account
aws organizations create-account \
  --email project-prod@yourcompany.com \
  --account-name "project-prod" \
  --profile org

# Move to appropriate OU based on environment
# For production:
aws organizations move-account \
  --account-id 123456789012 \
  --source-parent-id r-xxxx \
  --destination-parent-id $PROD_OU \
  --profile org

# For staging:
aws organizations move-account \
  --account-id 123456789013 \
  --source-parent-id r-xxxx \
  --destination-parent-id $STAGING_OU \
  --profile org
```

**StackSets automatically deploy to new accounts!**

---

### Step 7: Verify Automation

```bash
# Check StackSet instances deployed
aws cloudformation list-stack-instances \
  --stack-set-name pipeline-bootstrap \
  --profile org

# Switch to new account and verify resources
aws sts assume-role \
  --role-arn arn:aws:iam::NEW-ACCOUNT-ID:role/OrganizationAccountAccessRole \
  --role-session-name verify \
  --profile org

# List resources (should see bucket, roles, etc.)
aws s3 ls
aws iam list-roles | grep -E "(SAMDeployRole|cfn-exec-role)"
```

---

## GitHub Actions Deployment

In your project's `.github/workflows/deploy.yml`:

```yaml
name: Deploy to AWS
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: read

    steps:
      - uses: actions/checkout@v3

      - uses: aws-actions/configure-aws-credentials@v2
        with:
          role-to-assume: arn:aws:iam::ACCOUNT-ID:role/SAMDeployRole
          aws-region: us-east-1

      - run: sam deploy --no-confirm-changeset --no-fail-on-empty-changeset
```

---

## DNS Setup (Per Project)

For each project with a domain:

**Production account**:
```bash
# Create hosted zone for apex domain
aws route53 create-hosted-zone --name example.com --caller-reference $(date +%s)
```

**Staging account**:
```bash
# Create hosted zone for subdomain
aws route53 create-hosted-zone --name staging.example.com --caller-reference $(date +%s)
```

**In production account**, delegate to staging:
```bash
# Get staging nameservers and create NS record
# (See stacksets/dns/ for helper templates)
```

---

## What's Automated

### Production Accounts Get:
- ✅ S3 artifacts bucket (`aws-sam-cli-managed-*`)
- ✅ CloudFormation execution role
- ✅ GitHub OIDC provider + SAMDeployRole
- ✅ CloudWatch alarms for serverless
- ✅ Budget alerts + anomaly detection
- ✅ **Automated daily backups**
- ✅ **Centralized log aggregation**
- ✅ **Email notification on creation**
- ✅ Security baseline via SCPs

### Staging Accounts Get:
- ✅ S3 artifacts bucket
- ✅ CloudFormation execution role
- ✅ GitHub OIDC provider + SAMDeployRole
- ✅ CloudWatch alarms
- ✅ Budget alerts
- ✅ Security baseline via SCPs
- ❌ No backups (cost savings)
- ❌ No log aggregation (noise reduction)

### Sandbox Accounts Get:
- ❌ Nothing (complete freedom)

---

## Verification Checklist

After creating a new account:

- [ ] StackSet instances show `SUCCEEDED` status
- [ ] S3 bucket `aws-sam-cli-managed-{account}-{region}` exists
- [ ] IAM role `SAMDeployRole` exists
- [ ] IAM role `aws-sam-cli-cfn-exec-role` exists
- [ ] GitHub Actions can assume role and deploy
- [ ] Budget alerts are configured
- [ ] Cost anomaly detector is active

---

## Naming Conventions

- **Accounts**: `{project}-staging`, `{project}-prod`
- **OU Structure**:
  ```
  Workloads/
  ├── Production/   ({project}-prod accounts)
  └── Staging/      ({project}-staging accounts)
  ```
- **StackSets**: Numbered prefixes for clarity
  - `01-pipeline-bootstrap`
  - `02-github-oidc`
  - `03-monitoring`
  - `04-cost-management`
  - `05-account-notifications`
  - `06-log-aggregation`
  - `07-backup-strategy`
- **Staging subdomain**: `staging.{domain}.com`

---

---

## 🚀 Setting Up a New Project (Staging + Production)

This guide walks through creating AWS accounts for a new project with both staging and production environments. Accounts are automatically provisioned with all necessary resources based on their OU placement.

### Prerequisites
- Access to AWS Control Tower console (Management account)
- AWS CLI configured with `org` profile
- This infrastructure deployed (`make quickstart` completed)

### Method 1: Using AWS Console (Recommended)

#### Step 1: Create Staging Account
1. **Navigate to Control Tower Account Factory**
   - AWS Console → Control Tower → Account factory → Create account

2. **Fill in account details:**
   - Account name: `projectname-staging` (e.g., `myapp-staging`)
   - Account email: `projectname-staging@yourcompany.com`
   - AWS SSO email: Your admin email
   - AWS SSO first/last name: Your name
   - Organizational unit: **Workloads/Staging** (or just **Workloads** if nested OUs don't appear)
   - Click "Create account"

   **Note**: If Production/Staging OUs don't appear in the dropdown, place in Workloads and move later using the CLI commands below.

3. **Wait for provisioning** (~5 minutes)
   - Control Tower creates the account
   - StackSets auto-deploy pipeline resources
   - You'll receive email notification with .env config

#### Step 2: Create Production Account
1. **Return to Account Factory**
   - Create another account

2. **Fill in account details:**
   - Account name: `projectname-prod` (e.g., `myapp-prod`)
   - Account email: `projectname-prod@yourcompany.com`
   - AWS SSO email: Your admin email
   - AWS SSO first/last name: Your name
   - Organizational unit: **Workloads/Production**
   - Click "Create account"

3. **Wait for provisioning** (~5 minutes)
   - Production account gets full suite (backups, logging, etc.)
   - Email notification with .env config

### Method 2: Using AWS CLI

#### Quick Setup Script
```bash
# Set your project name
PROJECT="myapp"
COMPANY_EMAIL_DOMAIN="yourcompany.com"

# Create staging account
aws organizations create-account \
  --email "${PROJECT}-staging@${COMPANY_EMAIL_DOMAIN}" \
  --account-name "${PROJECT}-staging" \
  --profile org

# Create production account
aws organizations create-account \
  --email "${PROJECT}-prod@${COMPANY_EMAIL_DOMAIN}" \
  --account-name "${PROJECT}-prod" \
  --profile org

# Get account IDs (after ~5 minutes)
STAGING_ID=$(aws organizations list-accounts \
  --query "Accounts[?Name=='${PROJECT}-staging'].Id" \
  --output text --profile org)

PROD_ID=$(aws organizations list-accounts \
  --query "Accounts[?Name=='${PROJECT}-prod'].Id" \
  --output text --profile org)

echo "Staging Account: ${STAGING_ID}"
echo "Production Account: ${PROD_ID}"

# Get OU IDs (cached from initial setup)
STAGING_OU=$(aws organizations list-organizational-units-for-parent \
  --parent-id $(aws organizations list-roots --query 'Roots[0].Id' --output text --profile org) \
  --query "OrganizationalUnits[?Name=='Staging'].Id" \
  --output text --profile org)

PROD_OU=$(aws organizations list-organizational-units-for-parent \
  --parent-id $(aws organizations list-roots --query 'Roots[0].Id' --output text --profile org) \
  --query "OrganizationalUnits[?Name=='Production'].Id" \
  --output text --profile org)

# Move accounts to correct OUs
aws organizations move-account \
  --account-id "${STAGING_ID}" \
  --source-parent-id $(aws organizations list-roots --query 'Roots[0].Id' --output text --profile org) \
  --destination-parent-id "${STAGING_OU}" \
  --profile org

aws organizations move-account \
  --account-id "${PROD_ID}" \
  --source-parent-id $(aws organizations list-roots --query 'Roots[0].Id' --output text --profile org) \
  --destination-parent-id "${PROD_OU}" \
  --profile org

echo "✅ Accounts created and moved to correct OUs"
echo "⏳ StackSets will auto-deploy in ~5 minutes"
echo "📧 Check email for .env configurations"
```

### Post-Creation Setup

#### 1. Configure AWS CLI Profiles
```bash
# Add to ~/.aws/config
PROJECT="myapp"  # Your project name

cat >> ~/.aws/config << EOF

[profile ${PROJECT}-staging]
role_arn = arn:aws:iam::${STAGING_ID}:role/OrganizationAccountAccessRole
source_profile = org
region = us-east-1

[profile ${PROJECT}-prod]
role_arn = arn:aws:iam::${PROD_ID}:role/OrganizationAccountAccessRole
source_profile = org
region = us-east-1
EOF

# Test access
aws sts get-caller-identity --profile ${PROJECT}-staging
aws sts get-caller-identity --profile ${PROJECT}-prod
```

#### 2. Set Up Your Project Repository
Create `.env.staging` and `.env.prod` files in your project using configs from email notifications:

```bash
# .env.staging
AWS_ACCOUNT_ID=<staging-account-id>
AWS_REGION=us-east-1
AWS_PROFILE=myapp-staging
AWS_ROLE_ARN=arn:aws:iam::<staging-account-id>:role/SAMDeployRole
SAM_CLI_TELEMETRY=false
ARTIFACTS_BUCKET=aws-sam-cli-managed-<staging-account-id>-us-east-1
STACK_NAME=myapp-staging

# .env.prod
AWS_ACCOUNT_ID=<prod-account-id>
AWS_REGION=us-east-1
AWS_PROFILE=myapp-prod
AWS_ROLE_ARN=arn:aws:iam::<prod-account-id>:role/SAMDeployRole
SAM_CLI_TELEMETRY=false
ARTIFACTS_BUCKET=aws-sam-cli-managed-<prod-account-id>-us-east-1
STACK_NAME=myapp-prod
```

#### 3. Configure GitHub Actions
```yaml
# .github/workflows/deploy.yml
name: Deploy Application
on:
  push:
    branches: [main, staging]

jobs:
  deploy-staging:
    if: github.ref == 'refs/heads/staging'
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: read
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::STAGING_ID:role/SAMDeployRole
          aws-region: us-east-1
      - run: sam deploy --config-env staging

  deploy-production:
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: read
    steps:
      - uses: actions/checkout@v4
      - uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::PROD_ID:role/SAMDeployRole
          aws-region: us-east-1
      - run: sam deploy --config-env prod
```

#### 4. Deploy Your First Application
```bash
# Deploy to staging
sam deploy --guided --profile myapp-staging

# Deploy to production
sam deploy --guided --profile myapp-prod
```

### What Gets Auto-Provisioned

| Resource | Staging | Production | Purpose |
|----------|---------|------------|---------|
| S3 Artifacts Bucket | ✅ | ✅ | SAM/CFN deployments |
| GitHub OIDC + Roles | ✅ | ✅ | CI/CD authentication |
| CloudWatch Alarms | ✅ | ✅ | API/Lambda monitoring |
| Budget Alerts | ✅ | ✅ | Cost control |
| Backup Vaults | ❌ | ✅ | Automated backups |
| Log Aggregation | ❌ | ✅ | Centralized logging |
| Email Notifications | Auto | Auto | Account ready email |

### Verification Checklist
- [ ] Both accounts show in `aws organizations list-accounts --profile org`
- [ ] Accounts are in correct OUs (check AWS Console → Organizations)
- [ ] StackSet instances deployed: `make status`
- [ ] Received email notifications with .env configs
- [ ] Can assume roles: `aws sts get-caller-identity --profile PROJECT-staging`
- [ ] S3 buckets created: `aws s3 ls --profile PROJECT-staging`
- [ ] GitHub Actions can deploy (create a test PR)

### Troubleshooting

**Account creation stuck:**
- Check CloudFormation in management account for Control Tower stacks
- Account creation typically takes 5-20 minutes

**Production/Staging OUs don't appear in Account Factory:**
- Run `make bootstrap` to enable Control Tower baselines for nested OUs
- Wait 2-3 minutes for baseline enablement to complete
- Refresh Account Factory page
- If still not appearing, create in Workloads OU and move with CLI

**StackSets not deploying:**
- Verify account is in correct OU
- Run `make status` to check StackSet health
- Check CloudFormation StackSet operations for errors

**Can't assume role:**
- Ensure Control Tower provisioning completed
- Verify AWS SSO is configured for the account
- Check role exists: `aws iam get-role --role-name OrganizationAccountAccessRole --profile PROJECT-staging`

---

## Common Operations

### Check Status
```bash
make status  # Shows OUs, StackSets, and deployment health
```

### Create a New Account
1. Use Control Tower Account Factory (or AWS Organizations)
2. Choose the appropriate OU:
   - **Production** for production workloads
   - **Staging** for development/testing
   - **Sandbox** for experiments
3. Wait ~5 minutes for auto-provisioning
4. Check email for account details and .env configuration

### Update StackSets
```bash
make deploy  # Re-deploys with latest templates (idempotent)
```

### Clean Up
```bash
make destroy  # Removes all StackSets (requires confirmation)
```

---

## Troubleshooting

**StackSet instance failed:**
```bash
aws cloudformation describe-stack-set-operation \
  --stack-set-name pipeline-bootstrap \
  --operation-id xxxxx-xxxx-xxxx \
  --profile org
```

**Resources not appearing:**
- Wait 5-10 minutes (StackSets are eventually consistent)
- Check account is in correct OU
- Verify StackSet has auto-deployment enabled

**GitHub Actions can't assume role:**
- Verify GitHub org/repo in OIDC trust policy
- Check OIDC provider thumbprint is current
- Ensure workflow has `id-token: write` permission

---

## Next Steps

1. **Migrate existing workloads** - Create accounts via Account Factory
2. **Set up domains** - Use DNS helper templates
3. **Configure monitoring** - Customize CloudWatch alarms
4. **Tune budgets** - Adjust thresholds per account
5. **Add team members** - Grant SSO access to specific accounts
