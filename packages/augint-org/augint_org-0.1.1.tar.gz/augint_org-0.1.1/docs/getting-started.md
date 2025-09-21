# Getting Started Guide

This guide will help you set up aillc-org and deploy your first AWS landing zone in under 10 minutes.

## Prerequisites

Before you begin, ensure you have:

1. **AWS Control Tower** activated in your management account
2. **AWS SSO** configured with at least one user
3. **AWS CLI** installed and configured
4. **Python 3.9+** installed
5. **GitHub Account** (for CI/CD integration)

## Installation

### Using pip (recommended for users)

```bash
pip install augint-org
```

### Using uv (recommended for developers)

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and install
git clone https://github.com/svange/aillc-org.git
cd aillc-org
uv sync
```

## Initial Setup

### Step 1: Configure AWS Credentials

```bash
# Configure SSO profile
aws configure sso
# Profile name: org
# SSO start URL: https://your-sso-url.awsapps.com/start
# SSO Region: us-east-1
# SSO Registration Scopes: [Leave blank]

# Login to AWS
aws sso login --profile org
```

### Step 2: Set Environment Variables

Create a `.env` file in your project root:

```bash
# Required
GH_ACCOUNT=your-github-org
GH_REPO=aillc-org
NOTIFICATIONS_EMAIL=alerts@your-domain.com

# Optional (with defaults)
BUDGETS_MONTHLY_DEFAULT=1000
BUDGETS_ANOMALY_THRESHOLD=100
AWS_PROFILE=org
AWS_REGION=us-east-1
```

### Step 3: Bootstrap the Organization

```bash
# Quick setup (all-in-one)
make quickstart

# Or step-by-step:
make bootstrap  # Create OUs and enable baselines
make setup      # Create GitHub Actions role
make deploy     # Deploy all StackSets
make status     # Verify deployment
```

### Step 4: Configure GitHub Actions

After running `make setup`, copy the displayed role ARN and add it to GitHub:

```bash
# Using GitHub CLI
gh secret set AWS_ROLE_ARN --body 'arn:aws:iam::123456789012:role/OrgPipelineRole'

# Or manually in GitHub Settings > Secrets and variables > Actions
```

## Creating Your First Account

### Using the CLI

```bash
# Create a production account
ai-org account create \
  --name "MyApp-Prod" \
  --email "myapp-prod@example.com" \
  --ou "Production"

# Create a staging account
ai-org account create \
  --name "MyApp-Staging" \
  --email "myapp-staging@example.com" \
  --ou "Staging"
```

### Using AWS Control Tower Console

1. Navigate to Control Tower > Account Factory
2. Click "Create account"
3. Fill in:
   - Account name: `MyApp-Prod`
   - Account email: `myapp-prod@example.com`
   - IAM Identity Center user email: Your SSO user
   - Organizational unit: `Workloads/Production`
4. Click "Create account"

The account will be automatically provisioned with all necessary resources based on its OU placement.

## Verifying the Setup

### Check StackSet Status

```bash
# View all StackSets
ai-org stackset list

# Check specific StackSet
ai-org stackset status --name pipeline-bootstrap

# View StackSet instances
ai-org stackset instances --name pipeline-bootstrap
```

### Check Account Resources

```bash
# List all accounts
ai-org account list

# View account details
ai-org account status --account-id 123456789012
```

### Verify GitHub Actions

1. Push a change to your repository
2. Check Actions tab in GitHub
3. Verify the infrastructure pipeline runs successfully

## What Happens Automatically?

When you create a new account:

### Production Accounts (Workloads/Production)
- ✅ S3 bucket for deployments
- ✅ CloudFormation execution role
- ✅ GitHub OIDC provider
- ✅ SAMDeployRole for GitHub Actions
- ✅ CloudWatch alarms and dashboards
- ✅ Budget alerts ($1000/month default)
- ✅ Cost anomaly detection
- ✅ AWS Backup vault and plans
- ✅ Centralized logging to Log Archive

### Staging Accounts (Workloads/Staging)
- ✅ S3 bucket for deployments
- ✅ CloudFormation execution role
- ✅ GitHub OIDC provider
- ✅ SAMDeployRole for GitHub Actions
- ✅ Basic CloudWatch monitoring
- ✅ Budget alerts ($500/month)
- ❌ No backups (cost savings)
- ❌ No log aggregation

### Sandbox Accounts (Sandbox)
- ❌ No automatic resources
- Complete freedom for experimentation

## Next Steps

1. **Deploy an application**: Use `sam deploy` with the auto-created resources
2. **Set up SSO access**: Assign users to accounts via AWS SSO
3. **Configure monitoring**: Customize CloudWatch dashboards
4. **Review security**: Check Service Control Policies in `stacksets/scps/`

## Common Commands

```bash
# Account management
ai-org account list                    # List all accounts
ai-org account create --help          # Create account help
ai-org account move --help            # Move account between OUs

# SSO management
ai-org sso assign --help              # Assign SSO permissions
ai-org sso list-assignments --help    # View assignments

# StackSet management
ai-org stackset deploy --help         # Deploy a StackSet
ai-org stackset list                  # List all StackSets

# Configuration
ai-org config init                    # Initialize configuration
ai-org config validate                # Validate current config
```

## Troubleshooting

### Issue: StackSet deployment fails

```bash
# Check StackSet status
ai-org stackset status --name <stackset-name>

# View CloudFormation events
aws cloudformation describe-stack-events \
  --stack-name StackSet-<name> \
  --profile org
```

### Issue: GitHub Actions fails with permissions error

1. Verify the role ARN in GitHub secrets matches the deployed role
2. Check the trust relationship includes your GitHub organization
3. Ensure the repository name matches what's configured

### Issue: Can't access new account

1. Verify SSO assignment: `ai-org sso list-assignments --account-id <id>`
2. Assign permissions: `ai-org sso assign --account-id <id> --email your@email.com`
3. Refresh SSO portal and try again

## Getting Help

- 📖 [Full Documentation](README.md)
- 💬 [GitHub Discussions](https://github.com/svange/aillc-org/discussions)
- 🐛 [Report Issues](https://github.com/svange/aillc-org/issues)
- 📧 Email: sam@augmentingintegrations.com

---

Ready to dive deeper? Check out the [User Guide](user-guide.md) for comprehensive coverage of all features.
