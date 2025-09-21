import functools

import githubkit
import githubkit.versions.latest.models as ghm
from environs import env


@functools.cache
def _get_github_client() -> githubkit.GitHub:
    token: str | None = env.str("GH_TOKEN", None) or env.str("GITHUB_TOKEN", None)
    return githubkit.GitHub(token)


async def github_description(repository: str) -> str:
    gh: githubkit.GitHub = _get_github_client()
    owner: str
    repo: str
    owner, _, repo = repository.partition("/")
    full_repo: ghm.FullRepository = (
        await gh.rest.repos.async_get(owner, repo)
    ).parsed_data
    return full_repo.description or ""
