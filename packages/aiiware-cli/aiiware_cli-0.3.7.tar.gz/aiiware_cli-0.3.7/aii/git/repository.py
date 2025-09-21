"""Git repository operations and context collection."""

import subprocess
from pathlib import Path

from ..core.exceptions import GitCommandError


class GitRepository:
    """Lightweight helper for collecting git context."""

    def __init__(self, root: Path | None = None) -> None:
        self.root = Path(root) if root else Path.cwd()

    def _run(self, args: list[str], strip_output: bool = True) -> str:
        """Execute a git command and return stdout."""
        try:
            result = subprocess.run(
                ["git", *args],
                cwd=self.root,
                check=True,
                capture_output=True,
                text=True,
            )
        except FileNotFoundError as exc:
            raise GitCommandError("Git is not installed or not in PATH.") from exc
        except subprocess.CalledProcessError as exc:
            stderr = (exc.stderr or exc.stdout or "").strip()
            raise GitCommandError(stderr or "Git command failed.") from exc

        output = result.stdout
        return output.strip() if strip_output else output

    def is_repository(self) -> bool:
        """Return True if cwd is inside a git repository."""
        try:
            return self._run(["rev-parse", "--is-inside-work-tree"]).lower() == "true"
        except GitCommandError:
            return False

    def get_root(self) -> str | None:
        """Return repository root path if available."""
        try:
            return self._run(["rev-parse", "--show-toplevel"])
        except GitCommandError:
            return None

    def get_current_branch(self) -> str | None:
        """Return current branch name."""
        try:
            branch = self._run(["rev-parse", "--abbrev-ref", "HEAD"])
            return branch if branch != "HEAD" else None
        except GitCommandError:
            return None

    def get_status_short(self) -> str:
        """Return short status output including branch summary."""
        try:
            return self._run(["status", "--short", "--branch"], strip_output=False)
        except GitCommandError:
            return ""

    def get_staged_diff(self) -> str:
        """Return staged diff for the current repository."""
        return self._run(["diff", "--cached", "--no-color"], strip_output=False)

    def get_staged_stats(self) -> str:
        """Return staged diff statistics."""
        return self._run(["diff", "--cached", "--stat"], strip_output=False)

    def get_diff_range(self, revision_range: str) -> str:
        """Return diff for an explicit revision range expression."""
        return self._run(["diff", "--no-color", revision_range], strip_output=False)

    def get_diff_range_stats(self, revision_range: str) -> str:
        """Return diff stats for a revision range expression."""
        return self._run(["diff", "--stat", revision_range], strip_output=False)

    def get_diff_between(self, base: str, target: str = "HEAD") -> str:
        """Return diff between base and target revisions."""
        return self._run(["diff", "--no-color", base, target], strip_output=False)

    def get_diff_stats_between(self, base: str, target: str = "HEAD") -> str:
        """Return diff statistics between base and target."""
        return self._run(["diff", "--stat", base, target], strip_output=False)

    def get_log_since(self, base: str, limit: int = 10) -> str:
        """Return recent commits since base."""
        return self._run(
            ["log", "--oneline", f"--max-count={limit}", f"{base}..HEAD"],
            strip_output=False,
        )

    def ref_exists(self, ref: str) -> bool:
        """Return True if git ref can be resolved."""
        try:
            self._run(["rev-parse", "--verify", f"{ref}^{{commit}}"])
            return True
        except GitCommandError:
            return False

    def guess_default_base(self) -> str:
        """Return a sensible default base branch."""
        for candidate in ["origin/main", "origin/master", "main", "master"]:
            if self.ref_exists(candidate):
                return candidate
        return "origin/main"
