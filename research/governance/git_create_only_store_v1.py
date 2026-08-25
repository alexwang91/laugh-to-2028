from __future__ import annotations

"""Durable git-backed create-only store for CONTROLLED_RESEARCH_RUNNER_V1.

The store writes each governed key to its prospectively assigned remote branch.
It never force-updates a branch. Existing keys fail closed. Every successful
write is fetched back from the remote and byte-compared before returning.
"""

from pathlib import Path
from typing import Mapping
import os
import subprocess
import tempfile


class GitCreateOnlyStoreV1:
    def __init__(
        self,
        repo_path: Path,
        *,
        base_sha: str,
        key_branches: Mapping[str, str],
        remote: str = "origin",
    ) -> None:
        self.repo_path = Path(repo_path)
        self.base_sha = base_sha
        self.key_branches = dict(key_branches)
        self.remote = remote
        if len(base_sha) != 40 or any(c not in "0123456789abcdef" for c in base_sha):
            raise ValueError("INVALID_BASE_SHA")
        if not self.key_branches:
            raise ValueError("EMPTY_KEY_BRANCH_MAP")

    def _git(self, *args: str, input_bytes: bytes | None = None, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[bytes]:
        merged = os.environ.copy()
        if env:
            merged.update(env)
        return subprocess.run(
            ["git", *args],
            cwd=self.repo_path,
            input=input_bytes,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            env=merged,
        )

    def _branch_for(self, key: str) -> str:
        try:
            return self.key_branches[key]
        except KeyError as exc:
            raise KeyError(f"UNMAPPED_CREATE_ONLY_KEY:{key}") from exc

    def _remote_head(self, branch: str) -> str | None:
        proc = self._git("ls-remote", "--heads", self.remote, f"refs/heads/{branch}")
        text = proc.stdout.decode().strip()
        if not text:
            return None
        rows = [row for row in text.splitlines() if row.strip()]
        if len(rows) != 1:
            raise RuntimeError(f"AMBIGUOUS_REMOTE_BRANCH:{branch}")
        return rows[0].split()[0]

    def _fetch_commit(self, sha: str) -> None:
        self._git("fetch", "--no-tags", self.remote, sha)

    def _read_at(self, sha: str, key: str) -> bytes | None:
        self._fetch_commit(sha)
        proc = subprocess.run(
            ["git", "show", f"{sha}:{key}"],
            cwd=self.repo_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if proc.returncode != 0:
            return None
        return proc.stdout

    def exists(self, key: str) -> bool:
        branch = self._branch_for(key)
        head = self._remote_head(branch)
        return head is not None and self._read_at(head, key) is not None

    def _commit_with_file(self, parent: str, key: str, payload: bytes) -> str:
        self._fetch_commit(parent)
        blob = self._git("hash-object", "-w", "--stdin", input_bytes=payload).stdout.decode().strip()
        with tempfile.NamedTemporaryFile(prefix="git-create-only-index-", delete=False) as fh:
            index_path = fh.name
        try:
            os.unlink(index_path)
            env = {"GIT_INDEX_FILE": index_path}
            self._git("read-tree", parent, env=env)
            self._git("update-index", "--add", "--cacheinfo", f"100644,{blob},{key}", env=env)
            tree = self._git("write-tree", env=env).stdout.decode().strip()
            commit_env = {
                "GIT_AUTHOR_NAME": "controlled-research-runner",
                "GIT_AUTHOR_EMAIL": "controlled-research-runner@invalid.local",
                "GIT_COMMITTER_NAME": "controlled-research-runner",
                "GIT_COMMITTER_EMAIL": "controlled-research-runner@invalid.local",
            }
            return self._git(
                "commit-tree", tree, "-p", parent, "-m", f"controlled create-only: {key}", env=commit_env
            ).stdout.decode().strip()
        finally:
            try:
                os.unlink(index_path)
            except FileNotFoundError:
                pass

    def create_only(self, key: str, payload: bytes) -> None:
        branch = self._branch_for(key)
        old_head = self._remote_head(branch)
        if old_head is not None and self._read_at(old_head, key) is not None:
            raise FileExistsError(key)
        parent = old_head or self.base_sha
        commit = self._commit_with_file(parent, key, bytes(payload))
        if old_head is None:
            refspec = f"{commit}:refs/heads/{branch}"
            self._git("push", self.remote, refspec)
        else:
            # A normal fast-forward push preserves create-only semantics. Any
            # concurrent branch movement rejects the push instead of overwriting.
            self._git("push", self.remote, f"{commit}:refs/heads/{branch}")
        remote_head = self._remote_head(branch)
        if remote_head != commit:
            raise RuntimeError(f"REMOTE_VERIFY_HEAD_MISMATCH:{branch}")
        remote_payload = self._read_at(remote_head, key)
        if remote_payload != bytes(payload):
            raise RuntimeError(f"REMOTE_VERIFY_PAYLOAD_MISMATCH:{key}")
