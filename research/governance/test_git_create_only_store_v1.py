from __future__ import annotations

from pathlib import Path
import subprocess

import pytest

from research.governance.git_create_only_store_v1 import GitCreateOnlyStoreV1


def _run(cwd: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=cwd, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout.strip()


def _fixture(tmp_path: Path):
    remote = tmp_path / "remote.git"
    seed = tmp_path / "seed"
    work = tmp_path / "work"
    subprocess.run(["git", "init", "--bare", str(remote)], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.run(["git", "init", str(seed)], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    _run(seed, "config", "user.name", "test")
    _run(seed, "config", "user.email", "test@example.invalid")
    (seed / "README").write_text("base\n")
    _run(seed, "add", "README")
    _run(seed, "commit", "-m", "base")
    base = _run(seed, "rev-parse", "HEAD")
    _run(seed, "remote", "add", "origin", str(remote))
    _run(seed, "push", "origin", f"{base}:refs/heads/main")
    subprocess.run(["git", "clone", str(remote), str(work)], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return remote, work, base


def _remote_head(work: Path, branch: str) -> str:
    row = _run(work, "ls-remote", "--heads", "origin", f"refs/heads/{branch}")
    assert row
    return row.split()[0]


def test_marker_result_run_once_are_remote_verified_and_create_only(tmp_path: Path):
    _remote, work, base = _fixture(tmp_path)
    marker = "research/x/RUN_ATTEMPT.marker"
    result = "research/x/PRIMARY_RESULT.json"
    run_once = "research/x/RUN_ONCE.marker"
    store = GitCreateOnlyStoreV1(
        work,
        base_sha=base,
        key_branches={
            marker: "research/x-marker",
            result: "research/x-result",
            run_once: "research/x-result",
        },
    )
    assert store.exists(marker) is False
    assert store.exists(result) is False
    store.create_only(marker, b"marker\n")
    assert store.exists(marker) is True
    store.create_only(result, b"result\n")
    store.create_only(run_once, b"run-once\n")
    assert store.exists(result) is True
    assert store.exists(run_once) is True
    result_head = _remote_head(work, "research/x-result")
    assert _run(work, "show", f"{result_head}:research/x/PRIMARY_RESULT.json") == "result"
    assert _run(work, "show", f"{result_head}:research/x/RUN_ONCE.marker") == "run-once"
    with pytest.raises(FileExistsError):
        store.create_only(marker, b"replacement\n")
    with pytest.raises(FileExistsError):
        store.create_only(result, b"replacement\n")


def test_unmapped_key_fails_closed(tmp_path: Path):
    _remote, work, base = _fixture(tmp_path)
    store = GitCreateOnlyStoreV1(work, base_sha=base, key_branches={"known": "known-branch"})
    with pytest.raises(KeyError, match="UNMAPPED_CREATE_ONLY_KEY"):
        store.exists("unknown")
    with pytest.raises(KeyError, match="UNMAPPED_CREATE_ONLY_KEY"):
        store.create_only("unknown", b"x")


def test_existing_remote_key_is_detected_before_write(tmp_path: Path):
    _remote, work, base = _fixture(tmp_path)
    key = "research/x/RUN_ATTEMPT.marker"
    store = GitCreateOnlyStoreV1(work, base_sha=base, key_branches={key: "research/x-marker"})
    store.create_only(key, b"first\n")
    second = GitCreateOnlyStoreV1(work, base_sha=base, key_branches={key: "research/x-marker"})
    assert second.exists(key) is True
    with pytest.raises(FileExistsError):
        second.create_only(key, b"second\n")
