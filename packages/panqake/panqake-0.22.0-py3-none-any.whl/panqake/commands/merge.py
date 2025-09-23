"""Command for merging PRs and managing branches after merge."""

import sys

from panqake.utils.branch_operations import (
    fetch_latest_from_remote,
    return_to_branch,
    update_branch_with_conflict_detection,
)
from panqake.utils.config import (
    add_to_stack,
    get_child_branches,
    get_parent_branch,
    get_worktree_path,
    remove_from_stack,
)
from panqake.utils.git import (
    branch_exists,
    checkout_branch,
    delete_remote_branch,
    get_current_branch,
    run_git_command,
    validate_branch,
)
from panqake.utils.github import (
    branch_has_pr,
    check_github_cli_installed,
    get_pr_checks_status,
    update_pr_base,
)
from panqake.utils.github import (
    merge_pr as github_merge_pr,
)
from panqake.utils.questionary_prompt import (
    format_branch,
    print_formatted_text,
    prompt_confirm,
)
from panqake.utils.selection import select_from_options
from panqake.utils.status import status


def fetch_latest_base_branch(branch_name):
    """Fetch the latest base branch to ensure we're up to date."""
    parent_branch = get_parent_branch(branch_name)
    if not parent_branch:
        parent_branch = "main"  # Default to main if no parent found

    return fetch_latest_from_remote(parent_branch)


def update_pr_base_for_children(branch_name, parent_branch):
    """Update the PR base reference for all child branches.

    This must be done before deleting the parent branch to avoid closing child PRs.
    """
    children = get_child_branches(branch_name)
    if not children:
        return True

    with status("Updating PR base references for child branches...") as s:
        success = True
        for child in children:
            # Check if the child has a PR
            if branch_has_pr(child):
                s.update(f"Updating PR base for {child}...")
                if update_pr_base(child, parent_branch):
                    s.pause_and_print("[success]PR base updated successfully[/success]")
                else:
                    s.pause_and_print(
                        f"[warning]Warning: Failed to update PR base for '{child}'[/warning]"
                    )
                    success = False

            # Recursively update grandchildren
            update_pr_base_for_children(child, child)

    return success


def merge_pr(branch_name, merge_method="squash"):
    """Merge a PR using GitHub CLI."""
    # First check if the branch has a PR
    if not branch_has_pr(branch_name):
        print_formatted_text(
            f"[warning]Error: Branch '{branch_name}' does not have an open PR[/warning]"
        )
        return False

    print_formatted_text(
        f"[info]Merging PR for branch {branch_name} using merge method: {merge_method}[/info]"
    )

    # Execute GitHub CLI to merge the PR - do NOT delete the branch yet
    # We'll need to update child PR references first
    if github_merge_pr(branch_name, merge_method):
        print_formatted_text("[success]PR merged successfully[/success]")
        return True
    else:
        print_formatted_text(
            f"[warning]Error: Failed to merge PR for branch '{branch_name}'[/warning]"
        )
        return False


def update_child_branches(branch_name, parent_branch, current_branch):
    """Update child branches after a parent branch has been merged."""
    children = get_child_branches(branch_name)

    if not children:
        return True

    with status("Updating child branches...") as s:
        success = True
        for child in children:
            s.update(f"Updating {child} to use new base {parent_branch}...")

            checkout_branch(child)

            # Update the parent-child relationship
            add_to_stack(child, parent_branch)
            s.pause_and_print(
                f"[info]Updated branch relationship for {format_branch(child)}[/info]"
            )

            # Use the utility function for rebasing with conflict detection
            rebase_success, error_msg = update_branch_with_conflict_detection(
                child, parent_branch, abort_on_conflict=True
            )

            if not rebase_success:
                s.pause_and_print(f"[warning]{error_msg}[/warning]")
                success = False
                break

            # Recursively update this branch's children
            update_child_branches(child, child, current_branch)

    return success


def cleanup_local_branch(branch_name):
    """Delete the local branch after successful merge."""
    if branch_exists(branch_name):
        # Check if branch has a worktree that needs cleanup
        worktree_path = get_worktree_path(branch_name)

        # If branch has a worktree, inform user to manually delete it
        if worktree_path:
            print_formatted_text(
                f"\n[warning]Branch '{branch_name}' has a worktree at: {worktree_path}[/warning]"
            )
            print_formatted_text("[info]To complete cleanup, please:[/info]")
            print_formatted_text("[info]1. cd out of the worktree directory[/info]")
            print_formatted_text(f"[info]2. Run: pq delete {branch_name}[/info]")
            return False

        with status(f"Deleting local branch {branch_name}...") as s:
            # Make sure we're not on the branch we're trying to delete
            current = get_current_branch()
            if current == branch_name:
                parent = get_parent_branch(branch_name)
                if not parent:
                    parent = "main"  # Default to main if no parent

                s.update(f"Switching to {parent} before deletion...")
                checkout_branch(parent)

            # Delete the branch
            s.update(f"Deleting branch {branch_name}...")
            delete_result = run_git_command(["branch", "-D", branch_name])
            if delete_result is None:
                print_formatted_text(
                    f"[warning]Error: Failed to delete local branch '{branch_name}'[/warning]"
                )
                return False

            # Clean up stacks.json file by removing the branch
            stack_removal = remove_from_stack(branch_name)

        if stack_removal:
            print_formatted_text("[success]Local branch deleted successfully[/success]")
        else:
            print_formatted_text(
                "[warning]Local branch deleted but not found in stack metadata[/warning]"
            )

    return True


def get_merge_method():
    """Get the merge method from user selection."""
    merge_methods = ["squash", "rebase", "merge"]
    return select_from_options(merge_methods, "Select merge method:", default="squash")


def handle_pr_base_updates(branch_name, parent_branch, update_children):
    """Update PR base references for child branches."""
    if not update_children:
        return True

    update_pr_success = update_pr_base_for_children(branch_name, parent_branch)
    if not update_pr_success:
        print_formatted_text(
            "[warning]Warning: Some PR base references could not be updated[/warning]"
        )

    return update_pr_success


def handle_branch_updates(branch_name, parent_branch, current_branch, update_children):
    """Update child branches after merge."""
    if not update_children:
        return True

    update_success = update_child_branches(branch_name, parent_branch, current_branch)
    if not update_success:
        print_formatted_text("[warning]Failed to update all child branches.[/warning]")
        print_formatted_text("[info]You may need to resolve conflicts manually.[/info]")

    return update_success


def perform_merge_operations(
    branch_name,
    parent_branch,
    current_branch,
    merge_method,
    delete_branch,
    update_children,
):
    """Perform all merge related operations."""
    # Fetch latest from remote
    fetch_latest_base_branch(branch_name)

    # IMPORTANT: First, update PR base references for all child branches
    # This must be done before we delete the branch to avoid closing child PRs
    handle_pr_base_updates(branch_name, parent_branch, update_children)

    # Check if all required checks have passed
    checks_passed, failed_checks = get_pr_checks_status(branch_name)
    if not checks_passed:
        print_formatted_text(
            "[warning]Warning: Not all required checks have passed for this PR.[/warning]"
        )
        print_formatted_text("[warning]Failed checks:[/warning]")
        for check in failed_checks:
            print_formatted_text(f"[warning]  - {check}[/warning]")
        print("")
        if not prompt_confirm("Do you want to proceed with the merge anyway?"):
            print_formatted_text("[info]Merge cancelled.[/info]")
            return False

    # Merge the PR (without deleting the branch yet)
    merge_success = merge_pr(branch_name, merge_method)
    if not merge_success:
        print_formatted_text("[warning]Merge operation failed. Stopping.[/warning]")
        return False

    # Now it's safe to delete the remote branch
    if delete_branch:
        delete_remote_branch(branch_name)

    # Update child branches if requested
    handle_branch_updates(branch_name, parent_branch, current_branch, update_children)

    # Delete local branch if requested
    if delete_branch:
        cleanup_success = cleanup_local_branch(branch_name)
        if not cleanup_success:
            print_formatted_text("[warning]Failed to clean up local branch.[/warning]")

    # Return to original branch if it still exists, otherwise go to parent
    return_to_branch(current_branch, parent_branch)

    print_formatted_text("[success]Merge and branch management completed.[/success]")
    return True


def merge_branch(branch_name=None, delete_branch=True, update_children=True):
    """Merge a PR and manage the branch stack after merge."""
    # Check for GitHub CLI
    if not check_github_cli_installed():
        print_formatted_text(
            "[warning]Error: GitHub CLI (gh) is required but not installed.[/warning]"
        )
        print_formatted_text(
            "[info]Please install GitHub CLI: https://cli.github.com[/info]"
        )
        sys.exit(1)

    branch_name = validate_branch(branch_name)
    current_branch = get_current_branch()

    # Get parent branch
    parent_branch = get_parent_branch(branch_name)
    if not parent_branch:
        parent_branch = "main"  # Default to main if no parent

    # Show summary of what we're about to do
    print_formatted_text(
        f"[info]Preparing to merge PR: {parent_branch} ← {branch_name}[/info]"
    )

    # Ask for merge method
    merge_method = get_merge_method()

    # Ask for confirmation
    if not prompt_confirm("Do you want to proceed with the merge?"):
        print_formatted_text("[info]Merge cancelled.[/info]")
        return

    # Perform merge operations
    perform_merge_operations(
        branch_name,
        parent_branch,
        current_branch,
        merge_method,
        delete_branch,
        update_children,
    )
