import requests
from urllib.parse import urlparse
import re

def extract_repo_info(github_url):
    """Extract owner and repo name from GitHub URL."""
    parsed = urlparse(github_url)
    path_parts = parsed.path.strip('/').split('/')
    if len(path_parts) >= 2:
        return path_parts[0], path_parts[1]
    else:
        raise ValueError("Invalid GitHub URL format.")

def get_default_branch(owner, repo):
    """Get the default branch of the repository."""
    api_url = f"https://api.github.com/repos/{owner}/{repo}"
    response = requests.get(api_url)
    response.raise_for_status()
    return response.json()['default_branch']

def get_repo_tree(owner, repo, branch):
    """Get the full file tree of the repository."""
    api_url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
    response = requests.get(api_url)
    response.raise_for_status()
    return response.json()['tree']

def generate_raw_links(owner, repo, branch, tree):
    """Generate raw GitHub links for code files."""
    raw_base = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/"
    code_file_pattern = re.compile(r'\.(py|js|ts|java|cpp|c|cs|rb|go|rs|php|html|css|json|yaml|yml|xml)$', re.IGNORECASE)
    return [raw_base + item['path'] for item in tree if item['type'] == 'blob' and code_file_pattern.search(item['path'])]

def main(github_url):
    owner, repo = extract_repo_info(github_url)
    branch = get_default_branch(owner, repo)
    tree = get_repo_tree(owner, repo, branch)
    links = generate_raw_links(owner, repo, branch, tree)
    for link in links:
        print(link)

# Example usage
github_project_url = "https://github.com/Blurry2746/DivoomDND"
main(github_project_url)
