from __future__ import annotations

"""Git-backed create-only persistence for controlled research RUN gates.

Every create_only call creates exactly one commit, pushes it to the already
checked-out RUN branch, fetches that remote ref, and verifies the exact bytes
from the remote object before returning.  A rejected/non-fast-forward push or
remote verification mismatch raises immediately.
"""

from pathlib import Path
import os
import subprocess


class GitRemoteCreateOnlyStore:
    def __init__(self, repo_root: Path, branch: str, remote: str = "origin") -> None:
        self.repo_root = Path(repo_root).resolve()
        self.branch = branch
        self.remote = remote
        self._fetch()

    def _git(self, *args: str, capture: bool = True) -> subprocess.CompletedProcess[bytes]:
        return subprocess.run(
            ["git", *args],
            cwd=self.repo_root,
            check=True,
            stdout=subprocess.PIPE if capture else None,
            stderr=subprocess.PIPE if capture else None,
        )

    def _fetch(self) -> None:
        self._git("fetch", "--quiet", self.remote, f"refs/heads/{self.branch}:refs/remotes/{self.remote}/{self.branch}")

    def _validated_path(self, key: str) -> Path:
        rel = Path(key)
        if rel.is_absolute() or ".." in rel.parts or not rel.parts:
            raise ValueError(f"INVALID_STORE_KEY:{key}")
        path = (self.repo_root / rel).resolve()
        if self.repo_root not in path.parents:
            raise ValueError(f"INVALID_STORE_KEY:{key}")
        return path

    def exists(self, key: str) -> bool:
        self._validated_path(key)
        self._fetch()
        probe = subprocess.run(
            ["git", "cat-file", "-e", f"refs/remotes/{self.remote}/{self.branch}:{key}"],
            cwd=self.repo_root,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return probe.returncode == 0

    def create_only(self, key: str, payload: bytes) -> None:
        path = self._validated_path(key)
        self._fetch()
        if self.exists(key) or path.exists():
            raise FileExistsError(key)

        path.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
        try:
            with os.fdopen(fd, "wb") as handle:
                handle.write(bytes(payload))
                handle.flush()
                os.fsync(handle.fileno())
        except Exception:
            path.unlink(missing_ok=True)
            raise

        self._git("add", "--", key, capture=False)
        self._git("commit", "-m", f"0085 RUN create-only: {key}", capture=False)
        self._git("push", self.remote, f"HEAD:refs/heads/{self.branch}", capture=False)
        self._fetch()
        remote_payload = self._git("show", f"refs/remotes/{self.remote}/{self.branch}:{key}").stdout
        if remote_payload != bytes(payload):
            raise RuntimeError(f"REMOTE_VERIFICATION_MISMATCH:{key}")
