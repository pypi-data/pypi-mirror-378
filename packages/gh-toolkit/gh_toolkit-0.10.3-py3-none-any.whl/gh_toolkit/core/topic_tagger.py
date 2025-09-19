"""Topic tagging functionality for GitHub repositories."""

import time
from typing import Any

from rich.console import Console

from gh_toolkit.core.github_client import GitHubAPIError, GitHubClient

console = Console()


class TopicTagger:
    """Automatically add relevant topic tags to GitHub repositories using LLM analysis."""

    def __init__(
        self, github_client: GitHubClient, anthropic_api_key: str | None = None
    ):
        """Initialize with GitHub client and optional Anthropic API key."""
        self.client = github_client
        self.anthropic_api_key = anthropic_api_key

        if anthropic_api_key:
            try:
                from anthropic import Anthropic

                self._anthropic_client = Anthropic(api_key=anthropic_api_key)
            except ImportError:
                console.print(
                    "[yellow]⚠ Anthropic package not available. Install with: pip install anthropic[/yellow]"
                )
                self._anthropic_client = None
        else:
            self._anthropic_client = None

    def get_readme_content(self, owner: str, repo: str) -> str:
        """Fetch README content from repository."""
        try:
            readme_text = self.client.get_repo_readme(owner, repo)
            return readme_text[:5000]  # Limit to first 5000 chars to avoid token limits
        except (GitHubAPIError, KeyError, Exception):
            return ""

    def generate_topics_with_llm(
        self, repo_data: dict[str, Any], readme: str
    ) -> list[str]:
        """Use Claude to generate relevant topic tags."""
        if not self._anthropic_client:
            console.print(
                "[yellow]⚠ No Anthropic API key provided, falling back to rule-based topics[/yellow]"
            )
            return self._generate_fallback_topics(repo_data)

        # Prepare context for LLM
        languages = repo_data.get("languages", {})
        context = f"""
Repository: {repo_data.get("name", "")}
Description: {repo_data.get("description", "No description")}
Main Language: {repo_data.get("language", "Unknown")}
All Languages: {", ".join(languages.keys()) if languages else "Unknown"}
Stars: {repo_data.get("stargazers_count", 0)}
Forks: {repo_data.get("forks_count", 0)}

README excerpt:
{readme[:2000] if readme else "No README available"}
"""

        prompt = f"""Based on the following GitHub repository information, suggest 5-10 relevant topic tags that would help users discover this repository. Topics should be lowercase, use hyphens instead of spaces, and be commonly used GitHub topics.

{context}

Provide only the topic tags as a comma-separated list, nothing else. Focus on:
- Programming languages used
- Frameworks and libraries
- Problem domain/use case
- Project type (e.g., cli-tool, web-app, library)
- Key features or technologies

Topics:"""

        try:
            response = self._anthropic_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=200,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}],
            )

            # Parse topics from response
            response_content = response.content[0]
            topics_text = (
                getattr(response_content, "text", "").strip()
                if hasattr(response_content, "text")
                else ""
            )
            topics = [t.strip().lower() for t in topics_text.split(",") if t.strip()]

            # Filter and validate topics
            valid_topics: list[str] = []
            for topic in topics:
                # Basic validation
                if (
                    topic
                    and len(topic) <= 50
                    and topic.replace("-", "").replace("_", "").isalnum()
                    and not topic.startswith("-")
                    and not topic.endswith("-")
                ):
                    valid_topics.append(topic)

            return valid_topics[
                :10
            ]  # GitHub allows max 20 topics, but 10 is reasonable

        except Exception as e:
            console.print(f"[yellow]⚠ Error generating topics with LLM: {e}[/yellow]")
            return self._generate_fallback_topics(repo_data)

    def _generate_fallback_topics(self, repo_data: dict[str, Any]) -> list[str]:
        """Generate basic topics using rule-based approach when LLM is unavailable."""
        topics: list[str] = []

        # Add main language
        if repo_data.get("language"):
            lang = repo_data["language"].lower()
            lang_map = {
                "javascript": "javascript",
                "python": "python",
                "java": "java",
                "typescript": "typescript",
                "c++": "cpp",
                "c#": "csharp",
                "go": "golang",
                "rust": "rust",
                "php": "php",
                "ruby": "ruby",
                "swift": "swift",
                "kotlin": "kotlin",
                "dart": "dart",
                "scala": "scala",
                "r": "r-lang",
                "matlab": "matlab",
                "shell": "shell-script",
                "powershell": "powershell",
                "html": "html",
                "css": "css",
            }
            if lang in lang_map:
                topics.append(lang_map[lang])

        # Add additional languages
        for lang in repo_data.get("languages", {}).keys():
            lang_lower = lang.lower()
            if lang_lower == "jupyter notebook":
                topics.append("jupyter-notebook")
            elif lang_lower == "dockerfile":
                topics.append("docker")

        # Infer project type from description and name
        description = (repo_data.get("description") or "").lower()
        name = repo_data.get("name", "").lower()
        combined_text = f"{description} {name}"

        # Map GitHub API field names to our expected format
        # Stars and forks could be used for popularity-based topic suggestions
        # stars = repo_data.get('stargazers_count', 0)
        # forks = repo_data.get('forks_count', 0)

        # Common patterns
        patterns = {
            "cli": ["cli", "command-line", "terminal"],
            "web": ["web", "website", "webapp", "web-app"],
            "api": ["api", "rest", "graphql"],
            "library": ["library", "lib", "package"],
            "framework": ["framework"],
            "tool": ["tool", "utility", "utils"],
            "bot": ["bot", "discord", "telegram"],
            "game": ["game", "gaming"],
            "mobile": ["mobile", "android", "ios"],
            "desktop": ["desktop", "gui"],
            "machine-learning": [
                "ml",
                "machine-learning",
                "ai",
                "neural",
                "deep-learning",
            ],
            "data-science": ["data", "analysis", "visualization", "pandas", "numpy"],
            "blockchain": ["blockchain", "crypto", "bitcoin", "ethereum"],
            "devops": ["docker", "kubernetes", "ci", "cd", "deployment"],
            "education": ["tutorial", "learning", "course", "education"],
            "documentation": ["docs", "documentation", "readme"],
        }

        for topic, keywords in patterns.items():
            if any(keyword in combined_text for keyword in keywords):
                topics.append(topic)

        # Remove duplicates and limit
        unique_topics = list(dict.fromkeys(topics))
        return unique_topics[:8]

    def get_repo_topics(self, owner: str, repo: str) -> list[str]:
        """Get current topics for a repository."""
        try:
            return self.client.get_repo_topics(owner, repo)
        except GitHubAPIError:
            return []

    def update_repo_topics(self, owner: str, repo: str, topics: list[str]) -> bool:
        """Update repository topics on GitHub."""
        # GitHub topics must be lowercase and can contain hyphens
        cleaned_topics = [t.lower().replace(" ", "-") for t in topics]

        try:
            # Need to use PUT request with special headers for topics
            import requests

            url = f"https://api.github.com/repos/{owner}/{repo}/topics"
            headers = {
                "Authorization": f"token {self.client.token}",
                "Accept": "application/vnd.github.mercy-preview+json",  # Required for topics API
            }

            response = requests.put(
                url, headers=headers, json={"names": cleaned_topics}
            )
            response.raise_for_status()
            return True
        except Exception as e:
            console.print(f"[red]Error updating topics for {owner}/{repo}: {e}[/red]")
            return False

    def process_repository(
        self, owner: str, repo: str, dry_run: bool = False, force: bool = False
    ) -> dict[str, Any]:
        """Process a single repository for topic tagging."""
        repo_string = f"{owner}/{repo}"

        try:
            # Get repo info
            repo_data = self.client.get_repo_info(owner, repo)

            # Get additional repo metadata
            languages = self.client.get_repo_languages(owner, repo)
            repo_data["languages"] = languages

            # Get current topics
            current_topics = self.get_repo_topics(owner, repo)

            # Check if topics already exist and we're not forcing
            if current_topics and not force:
                return {
                    "repo": repo_string,
                    "status": "skipped",
                    "message": f"Repository already has {len(current_topics)} topics",
                    "current_topics": current_topics,
                }

            # Get additional context
            readme = self.get_readme_content(owner, repo)

            # Generate topics with LLM or fallback
            suggested_topics = self.generate_topics_with_llm(repo_data, readme)

            if not suggested_topics:
                return {
                    "repo": repo_string,
                    "status": "error",
                    "message": "Failed to generate topics",
                }

            # Merge with existing topics if forcing an update
            if force and current_topics:
                # Combine and deduplicate
                all_topics = list(dict.fromkeys(current_topics + suggested_topics))
                final_topics = all_topics[:20]  # GitHub max is 20 topics
            else:
                final_topics = suggested_topics

            result = {
                "repo": repo_string,
                "current_topics": current_topics,
                "suggested_topics": suggested_topics,
                "final_topics": final_topics,
            }

            # Update topics if not in dry run mode
            if not dry_run:
                if self.update_repo_topics(owner, repo, final_topics):
                    result.update(
                        {
                            "status": "success",
                            "message": f"Successfully updated with {len(final_topics)} topics",
                        }
                    )
                else:
                    result.update(
                        {"status": "error", "message": "Failed to update topics"}
                    )
            else:
                result.update(
                    {
                        "status": "dry_run",
                        "message": f"Would update with {len(final_topics)} topics",
                    }
                )

            return result

        except GitHubAPIError as e:
            return {
                "repo": repo_string,
                "status": "error",
                "message": f"GitHub API error: {e.message}",
            }
        except Exception as e:
            return {
                "repo": repo_string,
                "status": "error",
                "message": f"Unexpected error: {str(e)}",
            }

    def process_multiple_repositories(
        self,
        repo_list: list[tuple[str, str]],
        dry_run: bool = False,
        force: bool = False,
    ) -> list[dict[str, Any]]:
        """Process multiple repositories with rate limiting."""
        results: list[dict[str, Any]] = []

        for i, (owner, repo) in enumerate(repo_list, 1):
            console.print(
                f"\n[blue]Processing {i}/{len(repo_list)}: {owner}/{repo}[/blue]"
            )

            result = self.process_repository(owner, repo, dry_run, force)
            results.append(result)

            # Show result
            status = result["status"]
            message = result.get("message", "")

            if status == "success":
                console.print(f"[green]✓ {message}[/green]")
                if result.get("final_topics"):
                    console.print(
                        f"[dim]Topics: {', '.join(result['final_topics'])}[/dim]"
                    )
            elif status == "skipped":
                console.print(f"[yellow]⏭ {message}[/yellow]")
                if result.get("current_topics"):
                    console.print(
                        f"[dim]Current: {', '.join(result['current_topics'])}[/dim]"
                    )
            elif status == "dry_run":
                console.print(f"[cyan]🔍 {message}[/cyan]")
                if result.get("final_topics"):
                    console.print(
                        f"[dim]Would add: {', '.join(result['final_topics'])}[/dim]"
                    )
            else:  # error
                console.print(f"[red]✗ {message}[/red]")

            # Rate limiting - be conservative with API calls
            if i < len(repo_list):
                time.sleep(2)

        return results
