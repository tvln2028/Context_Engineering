"""Tool name mapping and tool filter helpers for the GitHub Agent capstone."""

from typing import List
from langchain_core.tools import BaseTool

# GitHub toolkit uses verbose display names. Map them to snake_case identifiers
# so agent tool calls are readable in logs and prompts.
TOOL_NAME_MAPPING = {
    "Get Issues": "get_issues",
    "Get Issue": "get_issue",
    "Comment on Issue": "comment_on_issue",
    "List open pull requests (PRs)": "list_open_pull_requests",
    "Get Pull Request": "get_pull_request",
    "Overview of files included in PR": "get_pr_files_overview",
    "Create Pull Request": "create_pull_request",
    "List Pull Requests' Files": "list_pr_files",
    "Create File": "create_file",
    "Read File": "read_file",
    "Update File": "update_file",
    "Delete File": "delete_file",
    "Overview of existing files in Main branch": "get_main_branch_files_overview",
    "Overview of files in current working branch": "get_current_branch_files_overview",
    "List branches in this repository": "list_branches",
    "Set active branch": "set_active_branch",
    "Create a new branch": "create_branch",
    "Get files from a directory": "get_directory_files",
    "Search issues and pull requests": "search_issues_and_prs",
    "Search code": "search_code",
    "Create review request": "create_review_request",
    "Get Latest Release": "get_latest_release",
    "Get Releases": "get_releases",
    "Get Release": "get_release",
}


def rename_tool(tool: BaseTool) -> BaseTool:
    """Rename a GitHub toolkit tool to its snake_case identifier."""
    if tool.name in TOOL_NAME_MAPPING:
        tool.name = TOOL_NAME_MAPPING[tool.name]
    return tool


def get_documentation_tools(tools: List[BaseTool]) -> List[BaseTool]:
    names = {
        "get_main_branch_files_overview",
        "get_current_branch_files_overview",
        "get_directory_files",
        "read_file",
        "create_file",
        "update_file",
        "create_branch",
        "set_active_branch",
        "search_code",
    }
    return [t for t in tools if t.name in names]


def get_release_tools(tools: List[BaseTool]) -> List[BaseTool]:
    names = {
        "get_latest_release",
        "get_releases",
        "list_open_pull_requests",
        "get_pr_files_overview",
        "read_file",
    }
    return [t for t in tools if t.name in names]


def get_issue_tools(tools: List[BaseTool]) -> List[BaseTool]:
    names = {
        "get_issues",
        "get_issue",
        "comment_on_issue",
        "search_issues_and_prs",
        "read_file",
    }
    return [t for t in tools if t.name in names]


def get_code_review_tools(tools: List[BaseTool]) -> List[BaseTool]:
    names = {
        "list_open_pull_requests",
        "get_pull_request",
        "get_pr_files_overview",
        "list_pr_files",
        "read_file",
        "search_code",
        "search_issues_and_prs",
        "create_review_request",
    }
    return [t for t in tools if t.name in names]


def get_coding_tools(tools: List[BaseTool]) -> List[BaseTool]:
    """Tools for implementing code changes and opening PRs."""
    names = {
        "get_main_branch_files_overview",
        "get_directory_files",
        "read_file",
        "search_code",
        "list_branches",
        "create_branch",
        "set_active_branch",
        "create_file",
        "update_file",
        "delete_file",
        "create_pull_request",
    }
    return [t for t in tools if t.name in names]
