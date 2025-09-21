import json
import os
from datetime import datetime

import boto3


def handler(event, context):
    """Process Control Tower account creation events."""
    sns = boto3.client("sns")
    org = boto3.client("organizations")
    cf = boto3.client("cloudformation")

    print(f"Received event: {json.dumps(event)}")

    # Parse the event
    detail = event.get("detail", {})
    service_event_details = json.loads(detail.get("serviceEventDetails", "{}"))

    # Extract account information
    account_id = (
        service_event_details.get("createManagedAccountStatus", {})
        .get("account", {})
        .get("accountId")
    )
    account_name = (
        service_event_details.get("createManagedAccountStatus", {})
        .get("account", {})
        .get("accountName")
    )

    if not account_id:
        print("No account ID found in event")
        return {"statusCode": 200}

    # Get account email
    try:
        account_info = org.describe_account(AccountId=account_id)
        account_email = account_info["Account"]["Email"]
    except Exception as e:
        print(f"Error getting account info: {e}")
        account_email = "Unknown"

    # Get OU information
    try:
        parents = org.list_parents(ChildId=account_id)
        ou_id = parents["Parents"][0]["Id"] if parents["Parents"] else "Unknown"

        if ou_id != "Unknown" and ou_id.startswith("ou-"):
            ou_info = org.describe_organizational_unit(OrganizationalUnitId=ou_id)
            ou_name = ou_info["OrganizationalUnit"]["Name"]
        else:
            ou_name = "Root" if ou_id.startswith("r-") else "Unknown"
    except Exception as e:
        print(f"Error getting OU info: {e}")
        ou_id = "Unknown"
        ou_name = "Unknown"

    # Build the notification message
    profile_name = account_name.lower().replace(" ", "-")

    message = []
    message.append("🎉 New AWS Account Created Successfully!")
    message.append("")
    message.append("=" * 43)
    message.append("")
    message.append("📋 ACCOUNT DETAILS")
    message.append(f"• Account Name: {account_name}")
    message.append(f"• Account ID: {account_id}")
    message.append(f"• Account Email: {account_email}")
    message.append(f"• Organization Unit: {ou_name} ({ou_id})")
    message.append(f"• Created: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
    message.append("")
    message.append("=" * 43)
    message.append("")
    message.append("⚙️ READY-TO-USE .ENV CONFIGURATION")
    message.append(f"AWS_ACCOUNT_ID={account_id}")
    message.append("AWS_REGION=us-east-1")
    message.append(f"AWS_PROFILE={profile_name}")
    message.append(f"AWS_ROLE_ARN=arn:aws:iam::{account_id}:role/SAMDeployRole")
    message.append("")
    message.append("=" * 43)
    message.append("")
    message.append("🚀 NEXT STEPS")
    message.append("1. Add the .env configuration to your project")
    message.append("2. Configure AWS CLI profile:")
    message.append(
        f"   aws configure set profile.{profile_name}.role_arn arn:aws:iam::{account_id}:role/OrganizationAccountAccessRole"
    )
    message.append(f"   aws configure set profile.{profile_name}.source_profile org")
    message.append("3. Test deployment:")
    message.append(f"   sam deploy --guided --profile {profile_name}")
    message.append("")
    message.append("=" * 43)
    message.append("")
    message.append("This account is ready for deployment via GitHub Actions! 🎊")

    message_text = "\n".join(message)

    # Send notification
    try:
        response = sns.publish(
            TopicArn=os.environ["SNS_TOPIC_ARN"],
            Subject=f"AWS Account Created: {account_name} ({account_id})",
            Message=message_text,
        )
        print(f"Notification sent: {response['MessageId']}")
    except Exception as e:
        print(f"Error sending notification: {e}")
        raise

    return {"statusCode": 200, "body": "Notification sent"}
