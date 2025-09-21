# SPEC — Control Tower + Direct StackSets Landing Zone

_Last updated: 2025-09-19_

This specification defines the exact StackSets and resources to deploy for automated account provisioning.

## 1. Organization Structure

### Control Tower Managed (Hands Off)
- Security OU (Audit and Log Archive accounts)
- Sandbox OU (unrestricted experimentation)
- Organization CloudTrail
- AWS Config aggregation
- IAM Identity Center instance
- Default Control Tower guardrails

### Custom OU Hierarchy
```
Root
├── Security (CT)
├── Sandbox (CT) ← No StackSets, no SCPs
└── Workloads ← SCPs applied here
    ├── Production ← All StackSets
    └── Staging ← Pipeline StackSets only
```

## 2. StackSet Deployment Strategy

| StackSet | Management | Workloads | Production Only |
|----------|------------|-----------|------------------|
| 01-pipeline-bootstrap | | ✅ | |
| 02-github-oidc | | ✅ | |
| 03-monitoring | | ✅ | |
| 04-cost-management | | ✅ | |
| 05-account-notifications | ✅ | | |
| 06-log-aggregation | | | ✅ |
| 07-backup-strategy | | | ✅ |

## 3. StackSets to Deploy

### 2.1 Pipeline Bootstrap (`pipeline-bootstrap`)

**Purpose**: Replicate `sam pipeline bootstrap` resources for every account

**Template Resources**:
```yaml
ArtifactsBucket:
  Type: AWS::S3::Bucket
  Properties:
    BucketName: !Sub 'aws-sam-cli-managed-${AWS::AccountId}-${AWS::Region}'
    VersioningConfiguration:
      Status: Enabled
    BucketEncryption:
      ServerSideEncryptionConfiguration:
        - ServerSideEncryptionByDefault:
            SSEAlgorithm: AES256

CloudFormationExecutionRole:
  Type: AWS::IAM::Role
  Properties:
    RoleName: aws-sam-cli-cfn-exec-role
    AssumeRolePolicyDocument:
      Statement:
        - Effect: Allow
          Principal:
            Service: cloudformation.amazonaws.com
          Action: sts:AssumeRole
        - Effect: Allow
          Principal:
            AWS: !Sub 'arn:aws:iam::${AWS::AccountId}:role/SAMDeployRole'
          Action: sts:AssumeRole
    ManagedPolicyArns:
      - arn:aws:iam::aws:policy/AdministratorAccess  # Scope down in production
```

**Deployment**:
- Target: Workloads OU
- Regions: us-east-1 (expand as needed)
- Auto-deployment: Enabled

### 2.2 GitHub OIDC (`github-oidc`)

**Purpose**: Enable GitHub Actions deployments

**Parameters**:
- `GitHubOrg`: Organization or username (default: svange)
- `RepoPattern`: Repository pattern (default: *)
- `BranchPattern`: Branch pattern (default: *)

**Template Resources**:
```yaml
GitHubOIDCProvider:
  Type: AWS::IAM::OIDCProvider
  Properties:
    Url: https://token.actions.githubusercontent.com
    ClientIdList:
      - sts.amazonaws.com
    ThumbprintList:
      - 6938fd4d98bab03faadb97b34396831e3780aea1
      - 1c58a3a8518e8759bf075b76b750d4f2df264fcd

SAMDeployRole:
  Type: AWS::IAM::Role
  Properties:
    RoleName: SAMDeployRole
    AssumeRolePolicyDocument:
      Statement:
        - Effect: Allow
          Principal:
            Federated: !GetAtt GitHubOIDCProvider.Arn
          Action: sts:AssumeRoleWithWebIdentity
          Condition:
            StringEquals:
              'token.actions.githubusercontent.com:aud': sts.amazonaws.com
            StringLike:
              'token.actions.githubusercontent.com:sub':
                - !Sub 'repo:${GitHubOrg}/${RepoPattern}:ref:refs/heads/${BranchPattern}'
                - !Sub 'repo:${GitHubOrg}/${RepoPattern}:environment:*'
    Policies:
      - PolicyName: SAMDeploymentPolicy
        PolicyDocument:
          Statement:
            - Effect: Allow
              Action:
                - iam:PassRole
              Resource: !Sub 'arn:aws:iam::${AWS::AccountId}:role/aws-sam-cli-cfn-exec-role'
            - Effect: Allow
              Action:
                - cloudformation:*
                - s3:*
                - lambda:*
                - apigateway:*
                - dynamodb:*
                - events:*
                - logs:*
                - iam:*
              Resource: '*'
```

**Deployment**:
- Target: Workloads OU
- Regions: us-east-1
- Auto-deployment: Enabled

### 2.3 Monitoring Baseline (`monitoring-baseline`)

**Purpose**: CloudWatch alarms for serverless workloads

**Parameters**:
- `AlarmEmail`: Email for alarm notifications
- `AlarmPrefix`: Prefix for alarm names (default: App)

**Template Resources**:
```yaml
AlarmTopic:
  Type: AWS::SNS::Topic
  Properties:
    Subscriptions:
      - Endpoint: !Ref AlarmEmail
        Protocol: email

LambdaErrorAlarm:
  Type: AWS::CloudWatch::Alarm
  Properties:
    AlarmName: !Sub '${AlarmPrefix}-Lambda-Errors'
    MetricName: Errors
    Namespace: AWS/Lambda
    Statistic: Sum
    Period: 300
    EvaluationPeriods: 1
    Threshold: 10
    AlarmActions:
      - !Ref AlarmTopic

APIGateway4xxAlarm:
  Type: AWS::CloudWatch::Alarm
  Properties:
    AlarmName: !Sub '${AlarmPrefix}-API-4xx'
    MetricName: 4XXError
    Namespace: AWS/ApiGateway
    Statistic: Sum
    Period: 300
    EvaluationPeriods: 2
    Threshold: 50
    AlarmActions:
      - !Ref AlarmTopic

DynamoDBThrottleAlarm:
  Type: AWS::CloudWatch::Alarm
  Properties:
    AlarmName: !Sub '${AlarmPrefix}-DynamoDB-Throttles'
    MetricName: UserErrors
    Namespace: AWS/DynamoDB
    Statistic: Sum
    Period: 300
    EvaluationPeriods: 1
    Threshold: 5
    AlarmActions:
      - !Ref AlarmTopic
```

**Deployment**:
- Target: Workloads OU
- Regions: us-east-1
- Auto-deployment: Enabled

### 2.4 Cost Management (`cost-management`)

**Purpose**: Budget alerts and anomaly detection

**Parameters**:
- `BudgetEmail`: Email for budget alerts
- `MonthlyBudget`: Monthly budget limit in USD (default: 1000)
- `BudgetThreshold`: Alert threshold percentage (default: 80)

**Template Resources**:
```yaml
MonthlyBudget:
  Type: AWS::Budgets::Budget
  Properties:
    Budget:
      BudgetName: !Sub '${AWS::AccountId}-Monthly'
      BudgetType: COST
      TimeUnit: MONTHLY
      BudgetLimit:
        Amount: !Ref MonthlyBudget
        Unit: USD
    NotificationsWithSubscribers:
      - Notification:
          NotificationType: ACTUAL
          ComparisonOperator: GREATER_THAN
          Threshold: !Ref BudgetThreshold
          ThresholdType: PERCENTAGE
        Subscribers:
          - SubscriptionType: EMAIL
            Address: !Ref BudgetEmail
      - Notification:
          NotificationType: FORECASTED
          ComparisonOperator: GREATER_THAN
          Threshold: 100
          ThresholdType: PERCENTAGE
        Subscribers:
          - SubscriptionType: EMAIL
            Address: !Ref BudgetEmail

AnomalyDetector:
  Type: AWS::CE::AnomalyMonitor
  Properties:
    MonitorName: !Sub '${AWS::AccountId}-AnomalyMonitor'
    MonitorType: DIMENSIONAL
    MonitorDimension: SERVICE

AnomalySubscription:
  Type: AWS::CE::AnomalySubscription
  Properties:
    SubscriptionName: !Sub '${AWS::AccountId}-AnomalyAlerts'
    Threshold: 100  # Alert on $100+ anomalies
    Frequency: DAILY
    MonitorArnList:
      - !GetAtt AnomalyDetector.Arn
    Subscribers:
      - Address: !Ref BudgetEmail
        Type: EMAIL
```

**Deployment**:
- Target: Workloads OU (both Production and Staging inherit)
- Regions: us-east-1 (Budgets are global)
- Auto-deployment: Enabled

### 3.5 Account Notifications (`account-notifications`)

**Purpose**: Email notification when new accounts are created with all resource details

**Template Resources**:
```yaml
AccountCreationRule:
  Type: AWS::Events::Rule
  Properties:
    EventPattern:
      source:
        - aws.controltower
      detail-type:
        - AWS Control Tower Account Factory Event
    State: ENABLED
    Targets:
      - Arn: !GetAtt NotificationFunction.Arn

NotificationFunction:
  Type: AWS::Lambda::Function
  Properties:
    Handler: index.handler
    Runtime: python3.11
    Code:
      # Collects StackSet outputs
      # Formats .env configuration
      # Sends email via SES/SNS
```

**Deployment**:
- Target: Management Account only
- Regions: us-east-1
- Auto-deployment: Not applicable (single account)

### 3.6 Log Aggregation (`log-aggregation`)

**Purpose**: Centralize application logs from Production accounts to Log Archive

**Template Resources**:
```yaml
LogStreamRole:
  Type: AWS::IAM::Role
  Properties:
    AssumeRolePolicyDocument:
      Statement:
        - Effect: Allow
          Principal:
            Service: logs.amazonaws.com

LogSubscriptionFilter:
  Type: AWS::Logs::SubscriptionFilter
  Properties:
    DestinationArn: !Sub 'arn:aws:logs:${AWS::Region}:${LogArchiveAccountId}:destination:CentralLogs'
    FilterPattern: ''  # All logs
    RoleArn: !GetAtt LogStreamRole.Arn
```

**Deployment**:
- Target: Production OU only
- Regions: us-east-1
- Auto-deployment: Enabled

### 3.7 Backup Strategy (`backup-strategy`)

**Purpose**: Automated backups for Production workloads

**Template Resources**:
```yaml
BackupVault:
  Type: AWS::Backup::BackupVault
  Properties:
    BackupVaultName: !Sub '${AWS::AccountId}-backup-vault'
    EncryptionKeyArn: !GetAtt BackupKey.Arn

BackupPlan:
  Type: AWS::Backup::BackupPlan
  Properties:
    BackupPlan:
      BackupPlanName: !Sub '${AWS::AccountId}-daily-backups'
      BackupPlanRule:
        - RuleName: DailyBackups
          TargetBackupVault: !Ref BackupVault
          ScheduleExpression: cron(0 5 ? * * *)
          Lifecycle:
            DeleteAfterDays: 30

BackupSelection:
  Type: AWS::Backup::BackupSelection
  Properties:
    BackupSelection:
      SelectionName: AllSupportedResources
      IamRoleArn: !GetAtt BackupRole.Arn
      ListOfTags:
        - ConditionType: STRINGEQUALS
          ConditionKey: Backup
          ConditionValue: true
```

**Deployment**:
- Target: Production OU only
- Regions: us-east-1
- Auto-deployment: Enabled

## 4. Service Control Policies

### 4.1 Workloads Baseline SCP

**File**: `stacksets/scps/workloads-baseline.json`

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyLeavingOrganization",
      "Effect": "Deny",
      "Action": "organizations:LeaveOrganization",
      "Resource": "*"
    },
    {
      "Sid": "DenyIAMUserCreation",
      "Effect": "Deny",
      "Action": [
        "iam:CreateUser",
        "iam:CreateAccessKey"
      ],
      "Resource": "*"
    },
    {
      "Sid": "RequireApprovedRegions",
      "Effect": "Deny",
      "NotAction": [
        "iam:*",
        "organizations:*",
        "route53:*",
        "cloudfront:*",
        "waf:*",
        "cloudwatch:*",
        "support:*",
        "trustedadvisor:*"
      ],
      "Resource": "*",
      "Condition": {
        "StringNotEquals": {
          "aws:RequestedRegion": [
            "us-east-1",
            "us-west-2"
          ]
        }
      }
    }
  ]
}
```

**Attachment**:
```bash
aws organizations create-policy \
  --name workloads-baseline \
  --type SERVICE_CONTROL_POLICY \
  --content file://workloads-baseline.json

aws organizations attach-policy \
  --policy-id p-xxxxxxxx \
  --target-id WORKLOADS_OU_ID
```

## 5. Deployment Order

Critical path for dependencies:

1. **Create OU Structure**
   - Create Workloads OU
   - Create Production OU (under Workloads)
   - Create Staging OU (under Workloads)

2. **Deploy to Management Account**
   - Deploy account-notifications (for visibility)

3. **Deploy to Workloads OU** (auto-deploys to both Production and Staging)
   - Deploy pipeline-bootstrap (creates S3 bucket and CFN role)
   - Deploy github-oidc (depends on CFN role)
   - Deploy monitoring-baseline
   - Deploy cost-management

4. **Deploy to Production OU only**
   - Deploy log-aggregation
   - Deploy backup-strategy

5. **Attach SCPs**
   - Attach workloads-baseline to Workloads OU (inherited by children)

## 6. Parameters Summary

| StackSet | Parameter | Default | Required | Description |
|----------|-----------|---------|----------|-------------|
| github-oidc | GitHubOrg | svange | Yes | GitHub organization/username |
| github-oidc | RepoPattern | * | No | Repository name pattern |
| github-oidc | BranchPattern | * | No | Branch name pattern |
| monitoring-baseline | AlarmEmail | - | Yes | Email for CloudWatch alarms |
| monitoring-baseline | AlarmPrefix | App | No | Prefix for alarm names |
| cost-management | BudgetEmail | - | Yes | Email for budget alerts |
| cost-management | MonthlyBudget | 1000 | No | Monthly budget in USD |
| cost-management | BudgetThreshold | 80 | No | Alert threshold percentage |

## 7. Validation Tests

After deployment to a new account:

```bash
# Test 1: Verify S3 bucket exists
aws s3 ls s3://aws-sam-cli-managed-ACCOUNT-us-east-1/

# Test 2: Verify roles exist
aws iam get-role --role-name SAMDeployRole
aws iam get-role --role-name aws-sam-cli-cfn-exec-role

# Test 3: Verify OIDC provider
aws iam list-open-id-connect-providers

# Test 4: Verify budget
aws budgets describe-budgets --account-id ACCOUNT

# Test 5: Test GitHub Actions deployment
# Create a test workflow and verify it can assume role
```

## 8. Resource Naming

Consistent naming across all accounts:

| Resource | Name Pattern | Example |
|----------|--------------|---------|
| S3 Bucket | aws-sam-cli-managed-{account}-{region} | aws-sam-cli-managed-123456789012-us-east-1 |
| CFN Exec Role | aws-sam-cli-cfn-exec-role | aws-sam-cli-cfn-exec-role |
| Deploy Role | SAMDeployRole | SAMDeployRole |
| Budget | {account}-Monthly | 123456789012-Monthly |
| Alarms | {prefix}-{service}-{metric} | App-Lambda-Errors |

## 9. Future Enhancements

Not included in v1 but could be added:

- **Session Manager**: For EC2 access without SSH
- **AWS Backup**: Automated backup policies
- **GuardDuty**: Threat detection
- **Security Hub**: Compliance dashboard
- **Inspector**: Vulnerability scanning
- **Access Analyzer**: External access review
- **CloudWatch Logs retention**: Auto-expire old logs
- **Cost allocation tags**: Mandatory tagging

## 10. Rollback Strategy

To remove StackSets:

```bash
# Delete instances first
aws cloudformation delete-stack-instances \
  --stack-set-name pipeline-bootstrap \
  --deployment-targets OrganizationalUnitIds=WORKLOADS_OU \
  --regions us-east-1 \
  --no-retain-stacks

# Then delete StackSet
aws cloudformation delete-stack-set \
  --stack-set-name pipeline-bootstrap
```

Resources in existing accounts remain unless `RetainStacksOnAccountRemoval=false`.
