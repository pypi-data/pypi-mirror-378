# ARCHITECTURE — Control Tower + Direct StackSets

_Last updated: 2025-09-19_

## System Architecture

```mermaid
flowchart TB
  subgraph CT_Foundation["Control Tower Foundation"]
    MGMT[Management Account<br/>226839593255]
    AUDIT[Audit Account]
    LOG[Log Archive Account]
  end

  subgraph Workloads_OU["Workloads OU"]
    AILLC_STG[aillc-staging]
    AILLC_PROD[aillc-prod]
    LLS_STG[lls-staging]
    LLS_PROD[lls-prod]
    FUTURE[(...future accounts)]
  end

  MGMT -->|Controls| AUDIT
  MGMT -->|Controls| LOG
  MGMT -->|Manages| Workloads_OU

  subgraph CT_Services["Control Tower Services"]
    SSO[IAM Identity Center]
    TRAIL[Org CloudTrail]
    CONFIG[AWS Config]
    GUARD[Guardrails]
  end

  MGMT --> CT_Services

  subgraph StackSets["Auto-Deployed StackSets"]
    SS1[Pipeline Bootstrap<br/>S3 + CFN Execution Role]
    SS2[GitHub OIDC<br/>Provider + Deploy Role]
    SS3[Monitoring<br/>CloudWatch Alarms]
    SS4[Cost Management<br/>Budgets + Anomaly Detection]
  end

  StackSets -->|Auto-deploys to| Workloads_OU

  style MGMT fill:#f9f,stroke:#333,stroke-width:4px
  style Workloads_OU fill:#bbf,stroke:#333,stroke-width:2px
  style StackSets fill:#bfb,stroke:#333,stroke-width:2px
```

## Account Creation Flow

```mermaid
sequenceDiagram
    participant User
    participant AccountFactory as Account Factory
    participant CT as Control Tower
    participant StackSets
    participant NewAccount as New Account

    User->>AccountFactory: Create account "project-staging"
    AccountFactory->>CT: Provision account
    CT->>NewAccount: Create with CT baseline
    CT->>NewAccount: Place in Workloads OU

    Note over StackSets: Auto-deployment triggers

    par Deploy Pipeline Bootstrap
        StackSets->>NewAccount: S3 bucket (aws-sam-cli-managed-*)
        StackSets->>NewAccount: CloudFormation execution role
    and Deploy GitHub OIDC
        StackSets->>NewAccount: OIDC provider
        StackSets->>NewAccount: SAMDeployRole
    and Deploy Monitoring
        StackSets->>NewAccount: CloudWatch alarms
        StackSets->>NewAccount: SNS topic
    and Deploy Cost Management
        StackSets->>NewAccount: Budget alerts
        StackSets->>NewAccount: Cost anomaly detector
    end

    Note over NewAccount: Ready for deployment in ~5 minutes
    User->>NewAccount: sam deploy via GitHub Actions
```

## Resource Relationships

```mermaid
graph TB
  subgraph GitHub Actions
    WF[Workflow]
  end

  subgraph Production Account
    OIDC_P[OIDC Provider]
    ROLE_P[SAMDeployRole]
    CFN_P[CFN Execution Role]
    S3_P[Artifacts Bucket]
    BACKUP[Backup Vault]
    LOGS[Log Stream]
    ALARM[CloudWatch Alarms]
    BUDGET[Budget Alerts]

    OIDC_P --> ROLE_P
    ROLE_P --> CFN_P
    ROLE_P --> S3_P
    CFN_P --> S3_P
    BACKUP -.->|Backs up| S3_P
    LOGS -.->|Streams to| LOG_ARCHIVE
  end

  subgraph Staging Account
    OIDC_S[OIDC Provider]
    ROLE_S[SAMDeployRole]
    CFN_S[CFN Execution Role]
    S3_S[Artifacts Bucket]
    ALARM_S[CloudWatch Alarms]
    BUDGET_S[Budget Alerts]

    OIDC_S --> ROLE_S
    ROLE_S --> CFN_S
    ROLE_S --> S3_S
    CFN_S --> S3_S
  end

  subgraph Central Services
    LOG_ARCHIVE[Log Archive Account]
    NOTIFY[Notification Lambda]
  end

  WF -->|Assumes| ROLE_P
  WF -->|Assumes| ROLE_S

  style WF fill:#f96
  style Production Account fill:#9f9
  style Staging Account fill:#ff9
  style Central Services fill:#99f
```

## DNS Architecture (Per Project)

```mermaid
graph TB
  subgraph Production Account
    PROD_ZONE[example.com<br/>Hosted Zone]
    PROD_NS[NS Record:<br/>staging.example.com]
  end

  subgraph Staging Account
    STG_ZONE[staging.example.com<br/>Hosted Zone]
    STG_ALIAS[ALIAS: staging.example.com<br/>→ CloudFront/ALB]
  end

  PROD_NS -->|Delegates to| STG_ZONE

  subgraph DNS Queries
    Q1[staging.example.com] -->|Resolved by| STG_ALIAS
    Q2[example.com] -->|Resolved by| PROD_ZONE
  end
```

## Key Design Decisions

### 1. Direct StackSets vs CfCT
- **Chosen**: Direct StackSets with auto-deployment
- **Rationale**: Eliminates 30+ CfCT pipeline resources, reduces complexity
- **Trade-off**: Less sophisticated deployment orchestration (acceptable for our scale)

### 2. Account-per-Environment
- **Pattern**: `{project}-staging`, `{project}-prod`
- **Benefits**: Complete isolation, clear billing, easy handoff
- **Cost**: ~$0 (AWS doesn't charge for accounts)

### 3. Auto-Deployment
- **Mechanism**: StackSets with `AutoDeployment=true`
- **Benefit**: Zero-touch account provisioning
- **SLA**: Resources ready in ~5 minutes

### 4. GitHub OIDC vs IAM Users
- **Chosen**: OIDC with short-lived tokens
- **Security**: No long-lived credentials
- **Enforced**: SCP blocks IAM user creation

## Security Boundaries

```mermaid
graph TB
  subgraph Organization Level
    SCP[Service Control Policies]
    SCP -->|Denies| IAM_USERS[IAM User Creation]
    SCP -->|Denies| LEAVE[Leaving Organization]
    SCP -->|Restricts| REGIONS[Non-approved Regions]
  end

  subgraph Account Level
    OIDC_TRUST[OIDC Trust Policy]
    OIDC_TRUST -->|Limits to| GH_ORG[GitHub Org: svange]
    OIDC_TRUST -->|Requires| TOKEN_AUD[Audience: sts.amazonaws.com]

    CFN_ROLE[CFN Execution Role]
    CFN_ROLE -->|Scoped to| SERVICES[Required Services Only]
  end

  subgraph Network Level
    CT_GUARD[Control Tower Guardrails]
    CT_GUARD -->|Enforces| VPC_FLOW[VPC Flow Logs]
    CT_GUARD -->|Requires| ENCRYPTION[Encryption at Rest]
  end
```

## Cost Controls

1. **Budget Alerts**: 80% and 100% thresholds per account
2. **Cost Anomaly Detection**: ML-based spike detection
3. **Account Isolation**: Runaway costs contained per environment
4. **Resource Tagging**: Enforced via StackSet parameters

## Monitoring Strategy

### Application Level (Auto-deployed)
- Lambda error rates and throttles
- API Gateway 4xx/5xx rates
- DynamoDB throttles and errors
- All alarms → SNS → Email

### Organization Level (Control Tower)
- CloudTrail for all API calls
- Config for compliance tracking
- GuardDuty for threat detection (optional)
- Security Hub aggregation (optional)

## Scaling Considerations

### Current Scale (Optimized For)
- 5-20 accounts
- 1-5 developers
- 10-50 deployments/day

### Growth Path
- Add per-team OUs when hiring
- Implement CfCT if needing complex workflows
- Add AWS SSO permission sets for granular access
- Consider AWS Control Tower AFT for Terraform users
