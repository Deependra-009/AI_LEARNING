from fastmcp import FastMCP
from github import Github, Auth
from dotenv import load_dotenv
import os

load_dotenv()

mcp = FastMCP("github")

auth = Auth.Token(
    os.getenv("GITHUB_TOKEN")
)

github = Github(auth=auth)


@mcp.tool
def list_repositories():
    """List all repositories of authenticated user"""

    repos = github.get_user().get_repos()

    return [
        {
            "name": repo.name,
            "private": repo.private,
            "url": repo.html_url,
        }
        for repo in repos
    ]


@mcp.tool
def my_profile():
    """Get authenticated GitHub profile"""

    user = github.get_user()

    return {
        "login": user.login,
        "name": user.name,
        "followers": user.followers,
        "following": user.following,
        "public_repos": user.public_repos,
        "profile_url": user.html_url,
    }


@mcp.tool
def latest_commits(repo_name: str):
    """
    Fetch the 10 most recent commits from a GitHub repository.

    Parameters:
        repo_name: Repository name

    Example:
        latest_commits("Library")
    """

    repo = github.get_user().get_repo(repo_name)

    commits = repo.get_commits()

    return [
        {
            "sha": c.sha,
            "message": c.commit.message,
        }
        for c in commits[:10]
    ]


if __name__ == "__main__":
    mcp.run()