import os
import re
from urllib.parse import quote

import requests
from dotenv import load_dotenv

load_dotenv()

README_MAX_CHARS = 4000
GITHUB_API_URL = "https://api.github.com"


class RepositoryNotFoundError(Exception):
    pass


class GitHubUnavailableError(Exception):
    pass


def fetch_readme(owner: str, repo: str) -> str:
    owner = owner.strip()
    repo = repo.strip()
    if (
        not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})", owner)
        or not re.fullmatch(r"[A-Za-z0-9._-]{1,100}", repo)
        or repo in {".", ".."}
    ):
        raise ValueError("A valid GitHub owner and repository are required")

    url = (
        f"{GITHUB_API_URL}/repos/{quote(owner, safe='')}/"
        f"{quote(repo, safe='')}/readme"
    )
    headers = {
        "Accept": "application/vnd.github.raw",
        "User-Agent": "lab10-github-import",
    }
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        response = requests.get(url, headers=headers, timeout=10)
    except requests.RequestException as error:
        raise GitHubUnavailableError("Unable to reach GitHub") from error

    if response.status_code == 404:
        raise RepositoryNotFoundError("GitHub repository or README not found")
    try:
        response.raise_for_status()
    except requests.RequestException as error:
        raise GitHubUnavailableError("GitHub could not return the README") from error

    return response.text[:README_MAX_CHARS]
