"""
This module contains the required logic to get the diff between two
git tags in the given repository.
"""

import os
import re
import subprocess
from dataclasses import dataclass
from typing import Dict, List, Union


CHANGES_LINES_LIMIT = 5_000
REL_PATHS = [
    "app/app.go",
    "CHANGELOG.md",
    "go.mod"
]
REL_PATH_UPGRADES = "app/upgrades"
IGNORED_PATTERNS = [
    r"constants.go$",
    "app/upgrades/.+_test.go$"
]


@dataclass
class DiffConfig:
    """
    Holds the required information of the diff to obtain.
    """

    llm: str
    from_version: str
    to_version: str
    repo: str
    working_dir: str


@dataclass
class DiffResult:
    """
    Contains the relevant information about the resulting
    diff information.
    """

    diff: Dict[str, List[str]]


def get_filtered_diff(dc: DiffConfig) -> DiffResult:
    """
    Returns the changed files with corresponding changes
    without those that only adjust import paths between major versions.

    E.g. changes from github.com/evmos/evmos/v16 to github.com/evmos/evmos/v17
    will be ignored.
    """
    result = get_diff(dc)

    filtered_diff = {}
    filtered_changes = []

    for file, changes in result.diff.items():
        if file not in REL_PATHS and not REL_PATH_UPGRADES in file:
            continue

        if any(re.search(file, pattern) for pattern in IGNORED_PATTERNS):
            continue

        filtered_changes = [
            change for change in changes if "github.com/evmos/evmos/v" not in change
        ]
        if len(filtered_changes) == 0:
            continue

        if len(filtered_changes) > CHANGES_LINES_LIMIT:
            print(f"skipping changes in {file}, which are exceeding the limit of {CHANGES_LINES_LIMIT} changes")

        filtered_diff[file] = "\n".join(filtered_changes)

    return DiffResult(filtered_diff)


def get_diff(dc: DiffConfig) -> DiffResult:
    """
    Returns the changed with corresponding changes
    between the versions to compare.
    """
    print(f"cloning repo into folder {dc.working_dir}")
    clone_repo(dc)

    return get_diff_in_folder(dc)


def get_diff_in_folder(dc: DiffConfig) -> Union[DiffResult, None]:
    """
    Gets the git diff in the given folder.
    """
    out = run_in_path(
        ["git", "--no-pager", "diff", dc.from_version, dc.to_version, "--name-only"],
        dc.working_dir,
    )
    if out.returncode or not out.stdout:
        raise ValueError(f"failed to get diff: {out.stderr}")

    out_diff = {}
    for rel_path in out.stdout.split():
        out_diff[rel_path.decode()] = (
            run_in_path(
                ["git", "--no-pager", "diff", dc.from_version, dc.to_version, rel_path],
                dc.working_dir,
            )
            .stdout.decode()
            .splitlines()
        )

    return DiffResult(diff=out_diff)


def run_in_path(args: List[str], path: str):
    """
    Executes the command in the given working directory.
    """
    source_dir = os.getcwd()

    os.chdir(path)
    out = subprocess.run(args, capture_output=True, check=False)
    os.chdir(source_dir)

    return out


def clone_repo(dc: DiffConfig) -> str:
    """
    Clones the git repository with the given url
    into a temporary folder for the script to execute in.
    """
    # TODO: only clone the needed tags
    subprocess.run(
        ["git", "clone", dc.repo, dc.working_dir], capture_output=True, check=False
    )
