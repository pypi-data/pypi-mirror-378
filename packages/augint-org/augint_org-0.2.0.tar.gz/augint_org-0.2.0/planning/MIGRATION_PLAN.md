# AWS Account Migration Plan

_Last updated: 2025-09-20_

This plan migrates existing AWS accounts into the Control Tower organization, starting with LLS (paying customer).

## Current State

### Organization (226839593255)
- ✅ Control Tower deployed with landing zone
- ✅ 3 OUs: Sandbox, Security (Audit/Log Archive), Workloads (empty)
- ✅ 6 custom StackSets deployed (auto-deployment enabled)
- ✅ workloads-baseline SCP attached to Workloads OU

### External Accounts (Not in Org)
| Account | ID | Key Resources | Migration Priority |
|---------|----|--------------|--------------------|
| LLS | 808171354870 | SAM apps, landlinescrubber.com domains | **HIGH (Paying Customer)** |
| Default/Personal | 330659553592 | Multiple projects, 4 domains, EC2 | Medium |
| Epsilon | 711387119017 | svrd.link domain | Low |

## Phase 1: LLS Migration (Priority)

### Step 1.1: Create New Accounts

```bash
# Initialize configuration (first time only)
ai-org config init
# Enter your SSO email when prompted

# Create lls-staging account
ai-org account create lls-staging lls-staging@augmentingintegrations.com --wait
# Account created: 123456789012
# SSO access granted to sam@augmentingintegrations.com
# StackSets deployed

# Create lls-prod account
ai-org account create lls-prod lls-prod@augmentingintegrations.com --wait
# Account created: 234567890123
# SSO access granted to sam@augmentingintegrations.com
# StackSets deployed

# Get account IDs for use in later steps
LLS_STAGING_ID=$(ai-org account get 123456789012 --json | jq -r .Id)
LLS_PROD_ID=$(ai-org account get 234567890123 --json | jq -r .Id)
```

### Step 1.2: Verify StackSet Deployment

```bash
# Check StackSet deployment status for both accounts
ai-org stackset status $LLS_STAGING_ID
# StackSet                     Status
# org-pipeline-bootstrap       CURRENT
# org-github-oidc             CURRENT
# org-monitoring              CURRENT
# org-cost-management         CURRENT

ai-org stackset status $LLS_PROD_ID
# StackSet                     Status
# org-pipeline-bootstrap       CURRENT
# org-github-oidc             CURRENT
# org-monitoring              CURRENT
# org-cost-management         CURRENT
```

### Step 1.3: Configure SSO Access

```bash
# SSO access is automatically configured during account creation
# To grant additional users access:
ai-org sso assign $LLS_STAGING_ID --principal developer@company.com
ai-org sso assign $LLS_PROD_ID --principal developer@company.com

# List SSO assignments
ai-org sso list $LLS_STAGING_ID
# PrincipalType  PrincipalId            PermissionSet          Status
# USER          a408f408-5031-7092     AWSAdministratorAccess Active
# USER          b509f509-6142-8093     AWSAdministratorAccess Active
```

### Step 1.4: Set Up DNS Structure

#### In lls-prod account (owns apex domain):
```bash
# Assume role into lls-prod
export AWS_PROFILE=lls-prod  # After configuring SSO

# Create hosted zone for apex domain
aws route53 create-hosted-zone \
  --name landlinescrubber.com \
  --caller-reference "migration-$(date +%s)" \
  --query 'HostedZone.Id' \
  --output text
```

#### In lls-staging account (owns subdomain):
```bash
# Assume role into lls-staging
export AWS_PROFILE=lls-staging  # After configuring SSO

# Create hosted zone for staging subdomain
STAGING_ZONE=$(aws route53 create-hosted-zone \
  --name staging.landlinescrubber.com \
  --caller-reference "migration-$(date +%s)" \
  --query 'HostedZone.Id' \
  --output text)

# Get NS records for delegation
aws route53 list-resource-record-sets \
  --hosted-zone-id $STAGING_ZONE \
  --query "ResourceRecordSets[?Type=='NS'].ResourceRecords[].Value" \
  --output json > staging-ns-records.json
```

#### Back in lls-prod account (create delegation):
```bash
export AWS_PROFILE=lls-prod

# Add NS delegation to staging
aws route53 change-resource-record-sets \
  --hosted-zone-id $PROD_ZONE_ID \
  --change-batch '{
    "Changes": [{
      "Action": "CREATE",
      "ResourceRecordSet": {
        "Name": "staging.landlinescrubber.com.",
        "Type": "NS",
        "TTL": 300,
        "ResourceRecords": [
          {"Value": "ns-xxx.awsdns-xx.net."},
          {"Value": "ns-yyy.awsdns-yy.com."},
          {"Value": "ns-zzz.awsdns-zz.org."},
          {"Value": "ns-www.awsdns-ww.co.uk."}
        ]
      }
    }]
  }'
```

### Step 1.5: Transfer Domain Registration

```bash
# From old LLS account
export AWS_PROFILE=lls

# Prepare for transfer
aws route53domains enable-domain-transfer-lock \
  --domain-name landlinescrubber.com

# Get transfer authorization code
aws route53domains retrieve-domain-auth-code \
  --domain-name landlinescrubber.com

# In lls-prod account - initiate transfer
export AWS_PROFILE=lls-prod

aws route53domains transfer-domain \
  --domain-name landlinescrubber.com \
  --auth-code "YOUR_AUTH_CODE" \
  --duration-in-years 1 \
  --admin-contact file://contact.json \
  --registrant-contact file://contact.json \
  --tech-contact file://contact.json
```

### Step 1.6: Deploy Applications with SAM

#### Staging Deployment:
```bash
# Clone your application repository
git clone https://github.com/svange/lls-api.git
cd lls-api

# Configure AWS profile
export AWS_PROFILE=lls-staging

# Deploy to staging
sam build
sam deploy \
  --stack-name lls-api \
  --s3-bucket aws-sam-cli-managed-${LLS_STAGING_ID}-us-west-2 \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides \
    Stage=staging \
    DomainName=staging.landlinescrubber.com
```

#### Production Deployment:
```bash
export AWS_PROFILE=lls-prod

# Deploy to production
sam build
sam deploy \
  --stack-name lls-api \
  --s3-bucket aws-sam-cli-managed-${LLS_PROD_ID}-us-west-2 \
  --capabilities CAPABILITY_IAM \
  --parameter-overrides \
    Stage=prod \
    DomainName=api.landlinescrubber.com
```

### Step 1.7: Update GitHub Actions

Update `.github/workflows/deploy.yml`:
```yaml
name: Deploy to AWS
on:
  push:
    branches:
      - main  # Deploy to prod
      - staging  # Deploy to staging

jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: read
    steps:
      - uses: actions/checkout@v3

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: |
            arn:aws:iam::${{
              github.ref == 'refs/heads/main' && secrets.PROD_ACCOUNT_ID ||
              secrets.STAGING_ACCOUNT_ID
            }}:role/SAMDeployRole
          aws-region: us-west-2

      - name: Deploy SAM Application
        run: |
          sam build
          sam deploy \
            --no-confirm-changeset \
            --no-fail-on-empty-changeset \
            --stack-name lls-api \
            --parameter-overrides Stage=${{
              github.ref == 'refs/heads/main' && 'prod' || 'staging'
            }}
```

Add secrets:
```bash
gh secret set PROD_ACCOUNT_ID --body "$LLS_PROD_ID"
gh secret set STAGING_ACCOUNT_ID --body "$LLS_STAGING_ID"
```

## Phase 2: Default/Personal Account Split

### Accounts to Create:
- `augint-staging`, `augint-prod` - Augmenting Integrations projects
- `portal-staging`, `portal-prod` - API Portal projects
- `personal-sandbox` - Personal experiments (Sandbox OU)

```bash
# Create augint accounts
ai-org account create augint-staging augint-staging@augmentingintegrations.com --wait
ai-org account create augint-prod augint-prod@augmentingintegrations.com --wait

# Create portal accounts
ai-org account create portal-staging portal-staging@augmentingintegrations.com --wait
ai-org account create portal-prod portal-prod@augmentingintegrations.com --wait

# Create personal sandbox (specify Sandbox OU)
SANDBOX_OU=$(aws organizations list-organizational-units-for-parent \
  --parent-id r-55d0 \
  --query "OrganizationalUnits[?Name=='Sandbox'].Id" \
  --output text)
ai-org account create personal-sandbox personal@augmentingintegrations.com \
  --ou $SANDBOX_OU --wait --skip-stacksets
```

### Migration Order:
1. Create all accounts ✓
2. Set up DNS for each project pair
3. Migrate applications using SAM
4. Transfer domains:
   - `aillc.link` → augint-prod
   - `portal.aillc.link` → portal-prod
   - `openbra.in` → personal or specific project
   - `vangefamily.com` → personal-sandbox

## Phase 3: Epsilon Account

Simple migration - only has `svrd.link` domain:
1. Transfer domain to appropriate account
2. Close epsilon account

## Verification Checklist

### Per Account:
- [ ] Account created and in correct OU
  ```bash
  ai-org account list --ou ou-55d0-workloads
  ```
- [ ] StackSets deployed successfully
  ```bash
  ai-org stackset status <account-id>
  ```
- [ ] SSO access configured
  ```bash
  ai-org sso list <account-id>
  ```
- [ ] Budget alerts received (check email)
- [ ] GitHub Actions can assume role (test deployment)

### Per Application:
- [ ] SAM application deployed
- [ ] API Gateway accessible
- [ ] Lambda functions working
- [ ] DynamoDB tables migrated
- [ ] S3 buckets accessible
- [ ] CloudWatch logs flowing

### DNS Verification:
- [ ] Domain transferred successfully
- [ ] Hosted zones created
- [ ] NS delegation working (staging subdomain)
- [ ] API endpoints resolving
- [ ] SSL certificates valid

## Rollback Procedures

### If Migration Fails:
1. **Keep old accounts running** - They're not in the org, won't be affected
2. **Delete new resources** in new accounts (CloudFormation stacks)
3. **Transfer domain back** if needed (or update nameservers)
4. **Update GitHub Actions** to point back to old accounts

### If Partially Successful:
1. **Run both in parallel** - Old and new accounts can coexist
2. **Use Route53 weighted routing** to gradually shift traffic
3. **Monitor CloudWatch metrics** in both accounts
4. **Complete migration when stable**

## Timeline Estimate

### LLS Migration:
- Account creation: 20 minutes
- DNS setup: 30 minutes
- Domain transfer: 24-48 hours (registrar dependent)
- Application deployment: 1 hour
- Testing & verification: 2 hours
- **Total: 1-2 days**

### Full Migration (All Accounts):
- LLS: 2 days
- Default/Personal split: 3-4 days
- Epsilon: 1 day
- **Total: 1 week**

## Post-Migration Cleanup

### Old Account Cleanup:
```bash
# Delete all CloudFormation stacks
aws cloudformation list-stacks --profile lls \
  --query "StackSummaries[?StackStatus!='DELETE_COMPLETE'].StackName" \
  --output text | xargs -I {} aws cloudformation delete-stack --stack-name {} --profile lls

# Delete S3 buckets (after emptying)
aws s3 ls --profile lls | awk '{print $3}' | xargs -I {} \
  aws s3 rb s3://{} --force --profile lls

# Delete IAM users
aws iam list-users --profile lls --query "Users[].UserName" --output text | \
  xargs -I {} aws iam delete-user --user-name {} --profile lls
```

## Notes

- **Domain Propagation**: DNS changes take 24-48 hours to fully propagate
- **Keep Old Accounts Running**: During migration for rollback capability
- **Test Thoroughly**: Each application in new environment before cutting over
- **Monitor Costs**: New accounts will have separate billing
- **Update Documentation**: Record new account IDs and resources
