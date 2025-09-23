# augint-org (ai-org) 🚀

**One-command AWS account provisioning with Control Tower integration and enterprise-grade automation.**

Create production-ready AWS accounts in seconds. They auto-configure based on their environment. No manual setup required.

## 📊 Project Health

[![Library Publishing](https://github.com/Augmenting-Integrations/aillc-org/actions/workflows/publish.yaml/badge.svg?branch=main)](https://github.com/Augmenting-Integrations/aillc-org/actions/workflows/publish.yaml)
[![Infrastructure](https://github.com/Augmenting-Integrations/aillc-org/actions/workflows/infrastructure.yaml/badge.svg?branch=main)](https://github.com/Augmenting-Integrations/aillc-org/actions/workflows/infrastructure.yaml)
[![PyPI](https://img.shields.io/pypi/v/augint-org?style=flat-square)](https://pypi.org/project/augint-org/)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg?style=flat-square)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)

| 📖 **[Documentation](https://augmenting-integrations.github.io/aillc-org)** | 🧪 **[Tests](https://augmenting-integrations.github.io/aillc-org/unit-test-report.html)** | 📊 **[Coverage](https://augmenting-integrations.github.io/aillc-org/htmlcov/index.html)** | 🔒 **[Security](https://augmenting-integrations.github.io/aillc-org/security-reports.html)** | ⚖️ **[Compliance](https://augmenting-integrations.github.io/aillc-org/license-compatibility.html)** |
|:-:|:-:|:-:|:-:|:-:|

## ✨ What Does It Do?

The `ai-org` CLI tool automates AWS multi-account management:

- **Creates accounts** with one command
- **Auto-provisions resources** based on environment (prod/staging/sandbox)
- **Sets up CI/CD** with GitHub Actions OIDC (no AWS keys!)
- **Configures monitoring, backups, and compliance** automatically
- **Sends email notifications** with ready-to-use configurations

## 🚀 Quick Start (5 minutes)

### 1. Install the CLI

```bash
# Install with pip (or pipx for isolation)
pip install augint-org

# Or with uv (recommended - 10-100x faster)
uv pip install augint-org
```

### 2. Configure Your Environment (Optional)

```bash
# Set your AWS profile (required)
export AWS_PROFILE=org

# Optional: Create personal defaults config
ai-org config init

# Or create manually at ~/.ai-org.env
cat > ~/.ai-org.env << EOF
AWS_PROFILE=org
DEFAULT_SSO_EMAIL=you@company.com
DEFAULT_PERMISSION_SET=AWSAdministratorAccess
NOTIFICATIONS_EMAIL=alerts@company.com
BUDGETS_MONTHLY_DEFAULT=1000
BUDGETS_ANOMALY_THRESHOLD=100
EOF

# Note: Environment variables override config file
```

### 3. Bootstrap Your Landing Zone

```bash
# One-time setup: Create OUs, deploy StackSets, configure policies
ai-org bootstrap

# This runs in minutes and sets up:
# ✅ OU structure (Workloads/Production, Workloads/Staging)
# ✅ 7 StackSets with auto-deployment
# ✅ Service Control Policies
# ✅ GitHub Actions authentication
# ✅ Cost management and monitoring
```

### 4. Create Your First Project

```bash
# Create both staging and production accounts for a project
ai-org account create myapp

# What happens automatically:
# 1. Creates myapp-staging account → Workloads/Staging OU
# 2. Creates myapp-prod account → Workloads/Production OU
# 3. Waits for Control Tower provisioning
# 4. StackSets auto-deploy appropriate resources
# 5. Emails you ready-to-use .env configurations
# 6. Sets up AWS CLI profiles automatically
```

### 5. Deploy Your Application

```bash
# Your accounts are ready! Deploy with SAM or CDK
cd your-app/
sam deploy --profile myapp-staging

# Or use GitHub Actions (already configured!)
git push origin staging
```

## 📋 What Gets Deployed Where

| Resource | Production | Staging | Sandbox |
|----------|------------|---------|----------|
| **S3 Deployment Bucket** | ✅ | ✅ | ❌ |
| **GitHub OIDC + Roles** | ✅ | ✅ | ❌ |
| **CloudWatch Monitoring** | ✅ | ✅ | ❌ |
| **Cost Alerts** | ✅ | ✅ | ❌ |
| **Automated Backups** | ✅ | ❌ | ❌ |
| **Centralized Logging** | ✅ | ❌ | ❌ |
| **Security Policies** | ✅ | ✅ | ❌ |

## 🎯 Common Commands

```bash
# Account Management
ai-org account create <project>           # Create staging + prod accounts
ai-org account create <project> --prod    # Create only production
ai-org account list                       # List all accounts
ai-org account info <project>             # Show account details

# Infrastructure Management
ai-org status                              # Show landing zone health
ai-org stackset list                       # List deployed StackSets
ai-org stackset update <name>              # Update a StackSet
ai-org validate                            # Validate all configurations

# Configuration
ai-org config show                         # Display current config
ai-org config set notifications.email x@y  # Update config value
ai-org config profiles add <name>          # Add AWS CLI profile

# Development
ai-org account sandbox <name>              # Create sandbox account
ai-org costs report --days 30              # Cost analysis
ai-org compliance check                    # Compliance report
```

## 🔧 GitHub Actions Setup

The bootstrap process creates a `SAMDeployRole` in each account. Your workflows just need:

```yaml
name: Deploy
on:
  push:
    branches: [main, staging]

jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: read

    steps:
      - uses: actions/checkout@v4

      - uses: aws-actions/configure-aws-credentials@v4
        with:
          # These are automatically created by ai-org!
          role-to-assume: ${{ vars.AWS_ROLE_ARN }}
          aws-region: us-east-1

      - run: sam deploy --config-env ${{ vars.ENVIRONMENT }}
```

## 🏗️ Architecture

```
Control Tower (AWS Managed)
├── Security OU
│   ├── Audit Account
│   └── Log Archive Account
├── Sandbox OU (Unrestricted)
└── Workloads OU (Your Domain)
    ├── Production OU
    │   └── [project]-prod accounts (Full automation)
    └── Staging OU
        └── [project]-staging accounts (Essential automation)
```

### Key Design Principles

1. **Zero-touch provisioning** - Accounts self-configure based on OU
2. **GitOps ready** - GitHub Actions OIDC from day one
3. **Cost conscious** - Staging gets essentials, prod gets everything
4. **Secure by default** - SCPs enforce security baseline
5. **Audit friendly** - Centralized logging and compliance reports

## 📚 Documentation

| Resource | Description |
|----------|-------------|
| **[API Reference](https://augmenting-integrations.github.io/aillc-org)** | Complete CLI and module documentation |
| **[Architecture Guide](docs/architecture.md)** | System design and decision rationale |
| **[Configuration Guide](docs/configuration.md)** | Detailed config options and examples |
| **[Migration Guide](MIGRATION_PLAN.md)** | Migrating existing accounts |
| **[Development Guide](docs/development.md)** | Contributing and local development |

## 🔍 Prerequisites

Before running `ai-org bootstrap`:

- ✅ AWS Control Tower is activated
- ✅ AWS SSO configured with management account access
- ✅ AWS CLI v2 with SSO profile configured
- ✅ Python 3.12+ installed
- ✅ GitHub organization created (for OIDC)

## 🚧 Troubleshooting

### Account Creation Issues

```bash
# Check account status
ai-org account info myapp --verbose

# View CloudFormation events
ai-org debug stackset-instances pipeline-bootstrap

# Verify OU structure
ai-org validate organization
```

### Common Issues

- **"Production OU not visible in Account Factory"** → Run `ai-org bootstrap --enable-baselines`
- **"StackSets not deploying"** → Check account is in correct OU with `ai-org account move`
- **"GitHub Actions can't authenticate"** → Verify with `ai-org validate github-oidc`

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](docs/contributing.md) for guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

Built with:
- [AWS Control Tower](https://aws.amazon.com/controltower/) for landing zone management
- [uv](https://github.com/astral-sh/uv) for blazing fast Python tooling
- [python-semantic-release](https://python-semantic-release.readthedocs.io/) for automated versioning
- [pdoc](https://pdoc.dev/) for documentation generation

---

<p align="center">
  <i>Stop clicking through AWS Console. Start shipping.</i>
</p>
