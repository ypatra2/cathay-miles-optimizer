"""
Git Manager — Handles creating branches and opening GitHub PRs
for the agentic engine refresh pipeline.

Uses PyGithub to execute all operations remotely via the GitHub REST API,
ensuring zero local file mutations natively inside Streamlit Cloud.
"""

import os
import subprocess
from datetime import datetime
from dotenv import load_dotenv

try:
    from github import Github, GithubException, InputGitTreeElement
except ImportError:
    Github = None
    InputGitTreeElement = None

load_dotenv()


def _get_repo_name() -> str:
    """Gets the repo name dynamically or falls back to hardcoded."""
    try:
        project_root = os.path.dirname(os.path.dirname(__file__))
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=project_root,
            capture_output=True,
            text=True
        )
        remote_url = result.stdout.strip()
        if "github.com" in remote_url:
            if remote_url.startswith("git@"):
                return remote_url.split(":")[-1].replace(".git", "")
            else:
                return remote_url.split("github.com/")[-1].replace(".git", "")
    except Exception:
        pass
    
    # Fallback to the known repo if subprocess fails (e.g., inside Streamlit Cloud container)
    return "ypatra2/cathay-miles-optimizer"


def create_refresh_branch(proposed_code: str, delta_report: str) -> dict:
    """
    Creates a new git branch remotely via GitHub API with the proposed optimizer.py
    changes and the delta report markdown. No local disk writes are performed.

    Returns:
        dict with keys: branch_name, success, error
    """
    month_tag = datetime.now().strftime("%Y-%m")
    branch_name = f"engine-refresh/{month_tag}"
    
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        return {
            "branch_name": branch_name,
            "success": False,
            "error": "GITHUB_TOKEN not found in environment. Please add it to your .env or Streamlit Secrets."
        }
    if not Github:
        return {
            "branch_name": branch_name,
            "success": False,
            "error": "PyGithub is not installed. Please add it to requirements.txt."
        }
    
    repo_name = _get_repo_name()
    g = Github(token)
    
    try:
        repo = g.get_repo(repo_name)
        main_ref = repo.get_git_ref("heads/main")
        
        # 1. Create a new branch pointing to main's SHA
        try:
            repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=main_ref.object.sha)
        except GithubException as e:
            if e.status == 422 and "Reference already exists" in str(e.data):
                # Branch exists! Append a timestamp string.
                branch_name = f"engine-refresh/{month_tag}-{int(datetime.now().timestamp())}"
                repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=main_ref.object.sha)
            else:
                raise

        # 2. Prepare multi-file commit via Git Trees API
        commit_message = f"feat(engine): agentic refresh {month_tag} via Deep Research Agent"
        main_commit = repo.get_commit(main_ref.object.sha)
        
        # We define the blobs that we want to push
        element_1 = InputGitTreeElement(
            path="optimizer.py",
            mode="100644",
            type="blob",
            content=proposed_code
        )
        element_2 = InputGitTreeElement(
            path=f"engine_deltas/engine_delta_{month_tag}.md",
            mode="100644",
            type="blob",
            content=delta_report
        )
        
        # 3. Create Tree and Commit
        base_tree = repo.get_git_tree(main_commit.sha)
        tree = repo.create_git_tree([element_1, element_2], base_tree=base_tree)
        parent = repo.get_git_commit(main_commit.sha)
        
        new_commit = repo.create_git_commit(commit_message, tree, [parent])
        
        # 4. Update Reference to point to new commit
        branch_ref = repo.get_git_ref(f"heads/{branch_name}")
        branch_ref.edit(new_commit.sha)

        return {
            "branch_name": branch_name,
            "success": True,
            "error": None
        }

    except Exception as e:
        return {
            "branch_name": branch_name,
            "success": False,
            "error": f"PyGithub API Error: {str(e)}"
        }


def create_github_pr(branch_name: str, patch_summary: str) -> dict:
    """
    Creates a GitHub Pull Request using PyGithub.
    
    Returns:
        dict with keys: pr_url, success, error, note
    """
    token = os.getenv("GITHUB_TOKEN")
    if not token or not Github:
        repo_name = _get_repo_name()
        compare_url = f"https://github.com/{repo_name}/compare/main...{branch_name}?expand=1"
        return {
            "pr_url": compare_url,
            "success": True,
            "error": None,
            "note": "No GITHUB_TOKEN set. Use the URL to manually create the PR."
        }
        
    repo_name = _get_repo_name()
    g = Github(token)
    
    try:
        repo = g.get_repo(repo_name)
        title = f"🔬 Engine Refresh — {datetime.now().strftime('%B %Y')}"
        body = (
            "## 🤖 Agentic Engine Refresh\n\n"
            "This PR was auto-generated by the **Deep Research + Dev Agent** pipeline.\n\n"
            f"### Changes Summary\n{patch_summary}\n\n"
            "### Review Checklist\n"
            "- [ ] Verify earn rate changes against official bank pages\n"
            "- [ ] Check that all function signatures are preserved\n"
            "- [ ] Run the Streamlit app to test recommendations\n"
        )
        
        pr = repo.create_pull(
            title=title,
            body=body,
            head=branch_name,
            base="main"
        )
        
        return {
            "pr_url": pr.html_url,
            "success": True,
            "error": None
        }

    except Exception as e:
        compare_url = f"https://github.com/{repo_name}/compare/main...{branch_name}?expand=1"
        return {
            "pr_url": compare_url,
            "success": True,
            "error": f"GitHub API call failed: {str(e)}. Use the URL to create PR manually."
        }
