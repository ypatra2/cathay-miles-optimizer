"""
Git Manager — Handles creating branches and opening GitHub PRs
for the agentic engine refresh pipeline.

Uses the GitHub REST API to create PRs programmatically.
"""

import os
import subprocess
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


def _run_git(args: list, cwd: str = None) -> tuple:
    """Run a git command and return (stdout, stderr, returncode)."""
    if cwd is None:
        cwd = os.path.dirname(os.path.dirname(__file__))
    result = subprocess.run(
        ["git"] + args,
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip(), result.stderr.strip(), result.returncode


def create_refresh_branch(proposed_code: str, delta_report: str) -> dict:
    """
    Creates a new git branch with the proposed optimizer.py changes,
    commits them, and pushes to origin.

    Returns:
        dict with keys: branch_name, success, error
    """
    project_root = os.path.dirname(os.path.dirname(__file__))
    month_tag = datetime.now().strftime("%Y-%m")
    branch_name = f"engine-refresh/{month_tag}"

    try:
        # Ensure we're on main and up to date
        _run_git(["checkout", "main"], cwd=project_root)
        _run_git(["pull", "origin", "main"], cwd=project_root)

        # Create and checkout new branch
        stdout, stderr, rc = _run_git(
            ["checkout", "-b", branch_name], cwd=project_root
        )
        if rc != 0 and "already exists" in stderr:
            # Branch exists, append timestamp
            branch_name = f"engine-refresh/{month_tag}-{int(datetime.now().timestamp())}"
            _run_git(["checkout", "-b", branch_name], cwd=project_root)

        # Write the proposed optimizer.py
        optimizer_path = os.path.join(project_root, "optimizer.py")
        with open(optimizer_path, "w") as f:
            f.write(proposed_code)

        # Write the delta report
        deltas_dir = os.path.join(project_root, "engine_deltas")
        os.makedirs(deltas_dir, exist_ok=True)
        report_path = os.path.join(deltas_dir, f"engine_delta_{month_tag}.md")
        with open(report_path, "w") as f:
            f.write(delta_report)

        # Stage and commit
        _run_git(["add", "optimizer.py", "engine_deltas/"], cwd=project_root)
        _run_git(
            ["commit", "-m",
             f"feat(engine): agentic refresh {month_tag} via Deep Research Agent"],
            cwd=project_root,
        )

        # Push to origin
        stdout, stderr, rc = _run_git(
            ["push", "-u", "origin", branch_name], cwd=project_root
        )
        if rc != 0:
            return {
                "branch_name": branch_name,
                "success": False,
                "error": f"Git push failed: {stderr}",
            }

        return {
            "branch_name": branch_name,
            "success": True,
            "error": None,
        }

    except Exception as e:
        return {
            "branch_name": branch_name,
            "success": False,
            "error": str(e),
        }
    finally:
        # Always clean up any dirty state and return to main
        _run_git(["reset", "--hard", "HEAD"], cwd=project_root)
        _run_git(["checkout", "main"], cwd=project_root)


def create_github_pr(branch_name: str, patch_summary: str) -> dict:
    """
    Creates a GitHub Pull Request using the GitHub REST API.

    Requires GITHUB_TOKEN in .env or environment.
    Falls back to returning a manual URL if no token is available.

    Returns:
        dict with keys: pr_url, success, error
    """
    github_token = os.getenv("GITHUB_TOKEN")

    # Get the repo owner/name from git remote
    project_root = os.path.dirname(os.path.dirname(__file__))
    stdout, _, _ = _run_git(["remote", "get-url", "origin"], cwd=project_root)
    remote_url = stdout.strip()

    # Parse owner/repo from remote URL
    # Handles both HTTPS and SSH formats
    if "github.com" in remote_url:
        if remote_url.startswith("git@"):
            # git@github.com:owner/repo.git
            parts = remote_url.split(":")[-1].replace(".git", "")
        else:
            # https://github.com/owner/repo.git
            parts = remote_url.split("github.com/")[-1].replace(".git", "")
        owner_repo = parts
    else:
        return {
            "pr_url": "",
            "success": False,
            "error": f"Cannot parse GitHub remote: {remote_url}",
        }

    if not github_token:
        # No token: return a manual compare URL
        compare_url = f"https://github.com/{owner_repo}/compare/main...{branch_name}?expand=1"
        return {
            "pr_url": compare_url,
            "success": True,
            "error": None,
            "note": "No GITHUB_TOKEN set. Use the URL to manually create the PR.",
        }

    # Create PR via GitHub API
    url = f"https://api.github.com/repos/{owner_repo}/pulls"
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json",
    }
    body = {
        "title": f"🔬 Engine Refresh — {datetime.now().strftime('%B %Y')}",
        "body": (
            "## 🤖 Agentic Engine Refresh\n\n"
            "This PR was auto-generated by the **Deep Research + Dev Agent** pipeline.\n\n"
            f"### Changes Summary\n{patch_summary}\n\n"
            "### Review Checklist\n"
            "- [ ] Verify earn rate changes against official bank pages\n"
            "- [ ] Check that all function signatures are preserved\n"
            "- [ ] Run the Streamlit app to test recommendations\n"
        ),
        "head": branch_name,
        "base": "main",
    }

    try:
        r = requests.post(url, headers=headers, json=body, timeout=15)
        if r.status_code == 201:
            pr_data = r.json()
            return {
                "pr_url": pr_data["html_url"],
                "success": True,
                "error": None,
            }
        else:
            # API PR creation failed, fall back to manual URL
            compare_url = f"https://github.com/{owner_repo}/compare/main...{branch_name}?expand=1"
            return {
                "pr_url": compare_url,
                "success": True,
                "error": f"GitHub API returned {r.status_code}: {r.text[:200]}. Use the URL to create PR manually.",
            }

    except Exception as e:
        compare_url = f"https://github.com/{owner_repo}/compare/main...{branch_name}?expand=1"
        return {
            "pr_url": compare_url,
            "success": True,
            "error": f"GitHub API call failed: {str(e)}. Use the URL to create PR manually.",
        }
