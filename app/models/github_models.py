from pydantic import BaseModel
from typing import Optional

class GitHubUser(BaseModel):
    login: str
    id: int

class GitHubHead(BaseModel):
    sha: str

class GitHubRepository(BaseModel):
    id: int
    name: str
    full_name: str
    owner: GitHubUser

class GitHubPullRequest(BaseModel):
    id: int
    number: int
    state: str
    title: str
    user: GitHubUser
    url: str
    diff_url: str
    html_url: str
    head: GitHubHead

class WebhookPayload(BaseModel):
    action: str
    number: Optional[int] = None
    pull_request: Optional[GitHubPullRequest] = None
    repository: GitHubRepository
    sender: GitHubUser