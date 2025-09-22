# Configuration Reference

This document covers all configuration options for aillc-org, including environment variables, user defaults, and runtime settings.

## Configuration Hierarchy

Configuration values are resolved in the following order (highest priority first):

1. **Command-line arguments** - Passed directly to CLI commands
2. **Environment variables** - Set in your shell or `.env` file
3. **Project `.env` file** - Project-specific settings
4. **User config file** - `~/.aillc/.env.aillc-org`
5. **Default values** - Built-in defaults

## Required Configuration

These settings must be configured before using aillc-org:

| Variable | Description | Example |
|----------|-------------|---------|
| `GH_ACCOUNT` | GitHub organization or username | `svange` |
| `GH_REPO` | GitHub repository name | `aillc-org` |
| `NOTIFICATIONS_EMAIL` | Email for AWS notifications | `alerts@example.com` |

## Optional Configuration

### AWS Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `AWS_PROFILE` | AWS CLI profile name | `org` |
| `AWS_REGION` | AWS region for deployments | `us-east-1` |
| `AWS_ACCOUNT_ID` | Management account ID | Auto-detected |

### Budget Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `BUDGETS_MONTHLY_DEFAULT` | Default monthly budget (USD) | `1000` |
| `BUDGETS_STAGING_MONTHLY` | Staging account budget | `500` |
| `BUDGETS_ANOMALY_THRESHOLD` | Anomaly detection threshold | `100` |
| `BUDGETS_ALERT_THRESHOLD` | Budget alert percentage | `80` |

### Control Tower Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `CT_HOME_REGION` | Control Tower home region | `us-east-1` |
| `CT_AUDIT_ACCOUNT` | Audit account name | `Audit` |
| `CT_LOG_ARCHIVE_ACCOUNT` | Log Archive account name | `Log Archive` |

### StackSet Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `STACKSET_ADMIN_ROLE` | StackSet administration role | `AWSControlTowerStackSetRole` |
| `STACKSET_EXEC_ROLE` | StackSet execution role | `AWSControlTowerExecution` |
| `STACKSET_CAPABILITIES` | CloudFormation capabilities | `CAPABILITY_NAMED_IAM` |

### GitHub Actions Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `GH_ROLE_NAME` | GitHub Actions role name | `OrgPipelineRole` |
| `GH_ROLE_SESSION_DURATION` | Session duration (seconds) | `3600` |
| `GH_BRANCH_PATTERN` | Allowed branches pattern | `main,dev,feat/*,fix/*` |

## Setting Up Configuration

### Method 1: Project .env File

Create a `.env` file in your project root:

```bash
# Required settings
GH_ACCOUNT=your-github-org
GH_REPO=your-repo-name
NOTIFICATIONS_EMAIL=alerts@your-domain.com

# AWS settings
AWS_PROFILE=org
AWS_REGION=us-east-1

# Budget settings
BUDGETS_MONTHLY_DEFAULT=2000
BUDGETS_ANOMALY_THRESHOLD=200

# Control Tower
CT_HOME_REGION=us-east-1
```

### Method 2: User Defaults

Create a user config file at `~/.aillc/.env.aillc-org`:

```bash
# User-specific defaults
GH_ACCOUNT=my-default-org
NOTIFICATIONS_EMAIL=my-default@email.com
AWS_PROFILE=my-default-profile

# These will be used for all aillc-org projects
# unless overridden by project .env or environment
```

### Method 3: Environment Variables

Set environment variables in your shell:

```bash
# Export for current session
export GH_ACCOUNT=your-github-org
export GH_REPO=your-repo-name
export NOTIFICATIONS_EMAIL=alerts@your-domain.com

# Or add to ~/.bashrc or ~/.zshrc for persistence
echo 'export AWS_PROFILE=org' >> ~/.bashrc
```

### Method 4: Command-line Arguments

Override any setting via CLI arguments:

```bash
# Override AWS profile
ai-org --profile production account list

# Override region
ai-org --region eu-west-1 stackset deploy

# Override GitHub settings
ai-org account create \
  --github-org different-org \
  --github-repo different-repo
```

## Configuration Validation

Validate your configuration:

```bash
# Check current configuration
ai-org config validate

# Show resolved configuration
ai-org config show

# Initialize configuration interactively
ai-org config init
```

## StackSet Template Variables

Variables available in CloudFormation templates:

| Variable | Description | Source |
|----------|-------------|--------|
| `GitHubOrg` | GitHub organization | `GH_ACCOUNT` |
| `GitHubRepo` | Repository name | `GH_REPO` |
| `NotificationEmail` | Alert email | `NOTIFICATIONS_EMAIL` |
| `MonthlyBudget` | Budget amount | `BUDGETS_MONTHLY_DEFAULT` |
| `AnomalyThreshold` | Anomaly threshold | `BUDGETS_ANOMALY_THRESHOLD` |

## Service Control Policy Variables

SCPs use these environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `ALLOWED_REGIONS` | Comma-separated region list | `us-east-1,us-west-2` |
| `ALLOWED_EC2_TYPES` | Allowed EC2 instance types | `t3.*,t4g.*` |
| `MAX_EC2_SIZE` | Maximum instance size | `xlarge` |
| `REQUIRE_MFA` | Require MFA for console | `true` |

## Cache Configuration

Cache behavior can be configured:

| Variable | Description | Default |
|----------|-------------|---------|
| `CACHE_TTL` | Cache time-to-live (seconds) | `3600` |
| `CACHE_DIR` | Cache directory | `~/.aillc/cache` |
| `DISABLE_CACHE` | Disable caching | `false` |

## CI/CD Configuration

GitHub Actions uses these secrets:

| Secret | Description | Required |
|--------|-------------|----------|
| `AWS_ROLE_ARN` | ARN of OrgPipelineRole | Yes |
| `GH_TOKEN` | GitHub PAT for releases | No |
| `SLACK_WEBHOOK` | Slack notifications | No |

## Security Configuration

### IAM Role Trust Policies

Configure trust relationships:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {
      "Federated": "arn:aws:iam::ACCOUNT:oidc-provider/token.actions.githubusercontent.com"
    },
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {
      "StringLike": {
        "token.actions.githubusercontent.com:sub": "repo:${GH_ACCOUNT}/${GH_REPO}:*"
      }
    }
  }]
}
```

### MFA Requirements

Enable MFA enforcement:

```bash
# Require MFA for production
export REQUIRE_MFA_PRODUCTION=true

# MFA age requirement (seconds)
export MFA_MAX_AGE=43200  # 12 hours
```

## Troubleshooting Configuration

### Debug Mode

Enable verbose logging:

```bash
# Enable debug output
export DEBUG=true
export LOG_LEVEL=debug

# Or via CLI
ai-org --debug account list
```

### Configuration Precedence Issues

Check which value is being used:

```bash
# Show configuration source
ai-org config show --verbose

# Test specific variable
ai-org config get GH_ACCOUNT --show-source
```

### Common Issues

1. **Variable not found**: Check spelling and hierarchy
2. **Wrong value used**: Higher precedence source may be set
3. **Cache issues**: Clear with `ai-org cache clear`
4. **Permission denied**: Check AWS credentials and profile

## Best Practices

1. **Use .env files** for project-specific settings
2. **Use user config** for personal defaults
3. **Never commit** `.env` files (use `.env.example`)
4. **Validate regularly** with `ai-org config validate`
5. **Document custom** variables in your README
6. **Use descriptive** variable names
7. **Set reasonable** defaults for optional values

## Example Configurations

### Minimal Configuration

```bash
# .env
GH_ACCOUNT=acme-corp
GH_REPO=infrastructure
NOTIFICATIONS_EMAIL=ops@acme.com
```

### Full Production Configuration

```bash
# .env
# GitHub Configuration
GH_ACCOUNT=acme-corp
GH_REPO=infrastructure
GH_BRANCH_PATTERN=main,release/*

# AWS Configuration
AWS_PROFILE=production
AWS_REGION=us-east-1
AWS_BACKUP_REGION=us-west-2

# Notifications
NOTIFICATIONS_EMAIL=ops@acme.com
SLACK_WEBHOOK_URL=https://hooks.slack.com/...

# Budgets
BUDGETS_MONTHLY_DEFAULT=5000
BUDGETS_STAGING_MONTHLY=1000
BUDGETS_DEV_MONTHLY=500
BUDGETS_ANOMALY_THRESHOLD=500
BUDGETS_ALERT_THRESHOLD=80

# Control Tower
CT_HOME_REGION=us-east-1
CT_AUDIT_ACCOUNT=audit
CT_LOG_ARCHIVE_ACCOUNT=logs

# Security
REQUIRE_MFA=true
MFA_MAX_AGE=28800
ALLOWED_REGIONS=us-east-1,us-west-2,eu-west-1

# Monitoring
ENABLE_ENHANCED_MONITORING=true
LOG_RETENTION_DAYS=90
METRIC_NAMESPACE=AcmeCorp

# Development
DEBUG=false
LOG_LEVEL=info
CACHE_TTL=7200
```

## Related Documentation

- [Environment Setup](development.md#environment-setup)
- [Security Best Practices](security.md#configuration-security)
- [CI/CD Configuration](deployment.md#github-actions-setup)
