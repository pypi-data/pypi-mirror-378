# CLI Specification for augint-org

## Overview

`augint-org` is a CLI tool for managing AWS Organization accounts with Control Tower. It automates the manual steps that Control Tower doesn't handle, particularly SSO permission assignment and StackSet deployment monitoring.

**Package name**: `augint-org` (on PyPI)
**CLI command**: `ai-org`
**Installation**: `pip install augint-org`

## Design Principles

1. **Resource-oriented**: Commands follow `ai-org <resource> <action>` pattern
2. **Convention over configuration**: Smart defaults with override capability
3. **Idempotent**: Safe to run multiple times
4. **Observable**: Clear feedback about operations
5. **Cacheable**: Reduces API calls through intelligent caching

## Command Structure

```
ai-org [global-options] <resource> <action> [action-options]
```

### Global Options
- `--profile TEXT`: AWS profile to use (default: from config or 'org')
- `--region TEXT`: AWS region (default: from config or 'us-east-1')
- `--debug`: Enable debug logging
- `--json`: Output in JSON format for automation

## Commands

### Account Management

#### `ai-org account create`
Create a new AWS account in the organization.

```bash
ai-org account create <name> <email> [OPTIONS]

Arguments:
  name    Account name (e.g., "lls-staging")
  email   Root email address for the account

Options:
  --ou TEXT           Target OU ID (default: Workloads OU from config)
  --wait              Wait for account creation to complete
  --skip-sso          Skip automatic SSO assignment
  --skip-stacksets    Skip waiting for StackSet deployment
```

Example:
```bash
ai-org account create lls-staging lls-staging@company.com --wait
```

#### `ai-org account list`
List accounts in the organization.

```bash
ai-org account list [OPTIONS]

Options:
  --ou TEXT         Filter by OU ID
  --status TEXT     Filter by status (ACTIVE, SUSPENDED)
```

#### `ai-org account get`
Get details for a specific account.

```bash
ai-org account get <account-id>
```

### SSO Management

#### `ai-org sso assign`
Assign SSO permissions to an account.

```bash
ai-org sso assign <account-id> [OPTIONS]

Arguments:
  account-id    AWS account ID (12 digits)

Options:
  --principal TEXT         Email or group name (default: from config)
  --permission-set TEXT    Permission set name (default: AWSAdministratorAccess)
  --principal-type TEXT    USER or GROUP (auto-detected if not specified)
```

The command will:
1. Use the principal email from `~/.aillc/config.yaml` if not specified
2. Look up the user/group ID in Identity Store
3. Assign the specified permission set to the account
4. Cache the assignment for future reference

Example:
```bash
# Uses email from config
ai-org sso assign 123456789012

# Explicit principal
ai-org sso assign 123456789012 --principal jane@company.com
```

#### `ai-org sso list`
List SSO assignments for an account.

```bash
ai-org sso list <account-id>
```

#### `ai-org sso sync`
Sync SSO permissions across multiple accounts.

```bash
ai-org sso sync [OPTIONS]

Options:
  --ou TEXT               Sync only accounts in this OU
  --permission-set TEXT   Which permission set to sync
  --principal TEXT        Principal to sync (default: from config)
```

### StackSet Management

#### `ai-org stackset status`
Check StackSet deployment status for an account.

```bash
ai-org stackset status <account-id> [OPTIONS]

Options:
  --stackset TEXT    Specific StackSet name (default: all)
  --wait            Wait for deployments to complete
```

#### `ai-org stackset list`
List all StackSets in the organization.

```bash
ai-org stackset list
```

### Configuration

#### `ai-org config init`
Initialize configuration file with interactive setup.

```bash
ai-org config init
```

This will:
1. Prompt for your SSO email
2. Discover SSO instance and Identity Store
3. Find default OU (Workloads)
4. Save configuration to `~/.aillc/config.yaml`

#### `ai-org config show`
Display current configuration.

```bash
ai-org config show
```

## Configuration File

Location: `~/.aillc/config.yaml`

```yaml
# User settings
sso:
  default_principal_email: sam@augmentingintegrations.com
  default_permission_set: AWSAdministratorAccess
  default_principal_type: USER

# AWS settings
defaults:
  ou: ou-55d0-nk2yt8m5          # Workloads OU
  region: us-east-1
  profile: org

# Cached values (auto-managed)
cache:
  sso_instance_arn: arn:aws:sso:::instance/ssoins-722360a7099ef9f4
  identity_store_id: d-90662739e9
  admin_group_id: c4c89498-a051-70ca-a80c-7b011c3b430a
  user_mappings:
    "sam@augmentingintegrations.com": "a408f408-5031-7092-4d31-6c7eeb81eca7"
  last_updated: 2024-01-20T10:30:00Z
```

## Output Formats

### Default (Human-Readable)
```
Creating account 'lls-staging'...
✅ Account created: 123456789012
⏳ Assigning SSO permissions...
✅ SSO access granted to sam@augmentingintegrations.com
⏳ Waiting for StackSets...
✅ StackSets deployed

Account ready for use!
```

### JSON Format (`--json`)
```json
{
  "account_id": "123456789012",
  "name": "lls-staging",
  "email": "lls-staging@company.com",
  "ou_id": "ou-55d0-nk2yt8m5",
  "sso_assigned": true,
  "stacksets_deployed": true
}
```

## Error Handling

All errors result in:
- Clear error message to stderr
- Suggested resolution
- Non-zero exit code

Common errors:
- `AWS credentials not configured`: Set AWS_PROFILE or use --profile
- `Account email already exists`: Use a different email address
- `SSO user not found`: Verify email exists in Identity Store
- `Permission set not found`: Check available sets with `ai-org config list-permission-sets`

## Environment Variables

The CLI respects these environment variables:
- `AWS_PROFILE`: Default AWS profile
- `AWS_REGION`: Default AWS region
- `AI_ORG_CONFIG`: Alternative config file location
- `AI_ORG_CACHE_TTL`: Cache TTL in seconds (default: 3600)

## Exit Codes

- `0`: Success
- `1`: General error
- `2`: AWS API error
- `3`: Configuration error
- `4`: Validation error
- `130`: Interrupted (Ctrl+C)

## Implementation Notes

### Package Structure
```
src/ai_org/
├── __init__.py
├── __version__.py       # Version: "0.1.0"
├── cli.py              # Main Click group
├── commands/
│   ├── __init__.py
│   ├── account.py      # Account commands
│   ├── sso.py         # SSO commands
│   ├── stackset.py    # StackSet commands
│   └── config.py      # Config commands
├── core/
│   ├── __init__.py
│   ├── aws_client.py  # Boto3 client management
│   ├── account_manager.py
│   ├── sso_manager.py
│   ├── stackset_manager.py
│   └── config_manager.py
└── utils/
    ├── __init__.py
    ├── output.py       # Output formatting
    ├── cache.py       # Caching logic
    └── validators.py  # Input validation
```

### Key Dependencies
- `click>=8.1`: CLI framework
- `boto3>=1.34`: AWS SDK
- `pyyaml>=6.0`: Config file parsing
- `python-dotenv>=1.0`: Environment management

## Usage Examples

### First Time Setup
```bash
# Install package
pip install augint-org

# Initialize configuration
ai-org config init
> Enter your SSO email: sam@augmentingintegrations.com
> Discovering SSO configuration...
> ✅ Configuration saved to ~/.aillc/config.yaml
```

### Create Account Pair
```bash
# Create staging account
ai-org account create myapp-staging myapp-staging@company.com --wait

# Create production account
ai-org account create myapp-prod myapp-prod@company.com --wait
```

### Grant Additional Access
```bash
# Grant access to another user
ai-org sso assign 123456789012 --principal developer@company.com

# List who has access
ai-org sso list 123456789012
```

### Monitor Deployments
```bash
# Check StackSet status
ai-org stackset status 123456789012

# Output:
# StackSet                     Status
# org-pipeline-bootstrap       SUCCEEDED
# org-github-oidc             SUCCEEDED
# org-monitoring              RUNNING
# org-cost-management         PENDING
```

## DNS Migration Process (Manual)

DNS operations are intentionally not automated. For domain migration:

1. Create accounts using `ai-org account create`
2. Transfer domain registration in AWS Console
3. Create hosted zones manually:
   ```bash
   aws route53 create-hosted-zone --name example.com
   ```
4. Set up delegation for staging subdomain
5. Update nameservers at registrar

See `MIGRATION_PLAN.md` for detailed DNS migration steps.
