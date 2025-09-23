"""Organizational Unit management commands."""

import click

from ai_org.core.ou_manager import OUManager


@click.group()
def ou() -> None:
    """Manage Organizational Units in the organization."""


@ou.command(name="list")
@click.option("--tree", is_flag=True, help="Display as tree structure (default)")
@click.option("--flat", is_flag=True, help="Display as flat list with paths")
@click.pass_context
def list_ous(ctx: click.Context, tree: bool, flat: bool) -> None:
    """List all OUs in the organization.

    \b
    Examples:
      ai-org ou list              # Display as tree (default)
      ai-org ou list --flat       # Display as flat list with paths
    """
    output = ctx.obj["output"]
    manager = OUManager(
        profile=ctx.obj.get("profile"),
        region=ctx.obj.get("region"),
    )

    try:
        if flat:
            # Show flat list
            ous = manager.list_ous()
            if ctx.obj.get("json"):
                output.json_output(ous)
            else:
                # Filter out ROOT for display
                ous_filtered = [ou for ou in ous if ou["Type"] != "ROOT"]
                output.table(
                    ous_filtered,
                    columns=["Id", "Name", "Path"],
                    title="Organizational Units",
                )
        else:
            # Show tree (default)
            ou_tree = manager.get_ou_tree()
            if ctx.obj.get("json"):
                output.json_output(ou_tree)
            else:
                output.info("Organization Structure:")
                tree_str = manager.format_ou_tree(ou_tree)
                output.text(tree_str)

    except Exception as e:
        output.error(f"Failed to list OUs: {e}")
        raise click.ClickException(str(e)) from e


@ou.command()
@click.argument("ou-id")
@click.pass_context
def get(ctx: click.Context, ou_id: str) -> None:
    """Get details for a specific OU.

    \b
    Arguments:
      OU-ID    Organizational Unit ID (e.g., ou-xxxx-yyyyyyyy)

    \b
    Example:
      ai-org ou get ou-55d0-production
    """
    output = ctx.obj["output"]
    manager = OUManager(
        profile=ctx.obj.get("profile"),
        region=ctx.obj.get("region"),
    )

    try:
        details = manager.get_ou_details(ou_id)

        if ctx.obj.get("json"):
            output.json_output(details)
        else:
            # Display OU info
            output.dict_display(
                {
                    "Id": details["Id"],
                    "Name": details["Name"],
                    "Arn": details["Arn"],
                    "Account Count": details["AccountCount"],
                    "Child OU Count": details["ChildOUCount"],
                },
                title=f"OU: {details['Name']}",
            )

            # Display accounts if any
            if details["Accounts"]:
                output.table(
                    details["Accounts"],
                    columns=["Id", "Name", "Email", "Status"],
                    title=f"Accounts in {details['Name']}",
                )

            # Display child OUs if any
            if details["ChildOUs"]:
                output.table(
                    details["ChildOUs"],
                    columns=["Id", "Name"],
                    title=f"Child OUs in {details['Name']}",
                )

    except Exception as e:
        output.error(f"Failed to get OU details: {e}")
        raise click.ClickException(str(e)) from e


@ou.command()
@click.argument("name")
@click.pass_context
def find(ctx: click.Context, name: str) -> None:
    """Find an OU by name and get its ID.

    \b
    Arguments:
      NAME    OU name to search for

    \b
    Example:
      ai-org ou find Production
    """
    output = ctx.obj["output"]
    manager = OUManager(
        profile=ctx.obj.get("profile"),
        region=ctx.obj.get("region"),
    )

    try:
        ou_id = manager.get_ou_by_name(name)

        if ou_id:
            if ctx.obj.get("json"):
                output.json_output({"Name": name, "Id": ou_id})
            else:
                output.success(f"Found OU '{name}': {ou_id}")
        else:
            output.warning(f"No OU found with name '{name}'")

            # Try to suggest similar OUs
            ous = manager.list_ous()
            similar = [
                ou for ou in ous if name.lower() in ou["Name"].lower() and ou["Type"] != "ROOT"
            ]

            if similar:
                output.info("\nDid you mean one of these?")
                for ou in similar:
                    output.text(f"  - {ou['Name']} ({ou['Id']})")

    except Exception as e:
        output.error(f"Failed to find OU: {e}")
        raise click.ClickException(str(e)) from e
