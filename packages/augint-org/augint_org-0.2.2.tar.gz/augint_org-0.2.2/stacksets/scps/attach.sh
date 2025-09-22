#!/bin/bash

# Service Control Policy attachment script
# This script creates and attaches the baseline SCP to the Workloads OU

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if AWS CLI is configured
if ! aws sts get-caller-identity --profile org &>/dev/null; then
    echo -e "${RED}Error: AWS CLI not configured or 'org' profile not found${NC}"
    echo "Please run: aws sso login --profile org"
    exit 1
fi

echo -e "${GREEN}Using AWS Account: $(aws sts get-caller-identity --query Account --output text --profile org)${NC}"

# Get or create Workloads OU
echo -e "\n${YELLOW}Looking for Workloads OU...${NC}"
WORKLOADS_OU=$(aws organizations list-organizational-units-for-parent \
    --parent-id $(aws organizations list-roots --query 'Roots[0].Id' --output text --profile org) \
    --query 'OrganizationalUnits[?Name==`Workloads`].Id' \
    --output text \
    --profile org)

if [ -z "$WORKLOADS_OU" ]; then
    echo -e "${YELLOW}Workloads OU not found. Would you like to create it? (y/n)${NC}"
    read -r CREATE_OU
    if [[ "$CREATE_OU" == "y" ]]; then
        ROOT_ID=$(aws organizations list-roots --query 'Roots[0].Id' --output text --profile org)
        WORKLOADS_OU=$(aws organizations create-organizational-unit \
            --parent-id "$ROOT_ID" \
            --name Workloads \
            --query 'OrganizationalUnit.Id' \
            --output text \
            --profile org)
        echo -e "${GREEN}Created Workloads OU: $WORKLOADS_OU${NC}"
    else
        echo -e "${RED}Cannot proceed without Workloads OU${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}Found Workloads OU: $WORKLOADS_OU${NC}"
fi

# Check if policy already exists
echo -e "\n${YELLOW}Checking for existing SCP...${NC}"
EXISTING_POLICY=$(aws organizations list-policies \
    --filter SERVICE_CONTROL_POLICY \
    --query 'Policies[?Name==`workloads-baseline`].Id' \
    --output text \
    --profile org)

if [ -n "$EXISTING_POLICY" ]; then
    echo -e "${YELLOW}Policy 'workloads-baseline' already exists with ID: $EXISTING_POLICY${NC}"
    echo "Would you like to update it? (y/n)"
    read -r UPDATE_POLICY
    if [[ "$UPDATE_POLICY" == "y" ]]; then
        aws organizations update-policy \
            --policy-id "$EXISTING_POLICY" \
            --content file://workloads-baseline.json \
            --profile org
        echo -e "${GREEN}Updated existing policy${NC}"
        POLICY_ID=$EXISTING_POLICY
    else
        POLICY_ID=$EXISTING_POLICY
    fi
else
    # Create the SCP
    echo -e "\n${YELLOW}Creating Service Control Policy...${NC}"
    POLICY_ID=$(aws organizations create-policy \
        --name workloads-baseline \
        --description "Baseline security controls for workload accounts" \
        --type SERVICE_CONTROL_POLICY \
        --content file://workloads-baseline.json \
        --query 'Policy.PolicySummary.Id' \
        --output text \
        --profile org)
    echo -e "${GREEN}Created SCP with ID: $POLICY_ID${NC}"
fi

# Check if already attached
echo -e "\n${YELLOW}Checking if policy is already attached...${NC}"
ATTACHED=$(aws organizations list-policies-for-target \
    --target-id "$WORKLOADS_OU" \
    --filter SERVICE_CONTROL_POLICY \
    --query "Policies[?Id=='$POLICY_ID'].Id" \
    --output text \
    --profile org)

if [ -n "$ATTACHED" ]; then
    echo -e "${GREEN}Policy is already attached to Workloads OU${NC}"
else
    # Attach to Workloads OU
    echo -e "\n${YELLOW}Attaching SCP to Workloads OU...${NC}"
    aws organizations attach-policy \
        --policy-id "$POLICY_ID" \
        --target-id "$WORKLOADS_OU" \
        --profile org
    echo -e "${GREEN}Successfully attached SCP to Workloads OU${NC}"
fi

# List accounts in Workloads OU
echo -e "\n${YELLOW}Accounts in Workloads OU that will be affected:${NC}"
aws organizations list-accounts-for-parent \
    --parent-id "$WORKLOADS_OU" \
    --query 'Accounts[].{Name:Name,Id:Id,Email:Email}' \
    --output table \
    --profile org

echo -e "\n${GREEN}✓ Service Control Policy setup complete!${NC}"
echo -e "Policy ID: $POLICY_ID"
echo -e "Workloads OU: $WORKLOADS_OU"
echo -e "\n${YELLOW}Note: SCP changes may take up to 5 minutes to propagate${NC}"
