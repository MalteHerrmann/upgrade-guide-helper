"""
This module contains the required logic to get the diff between two
git tags in the given repository.
"""

import os
import subprocess
from dataclasses import dataclass
from typing import Dict, List, Union


@dataclass
class DiffConfig:
    """
    Holds the required information of the diff to obtain.
    """

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
        filtered_changes = [
            change for change in changes if "github.com/evmos/evmos/v" not in change
        ]
        if len(filtered_changes) == 0:
            continue
        filtered_diff[file] = filtered_changes

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
    if not out:
        raise ValueError("failed to get diff")

    out_diff = {}
    for rel_path in out.split():
        out_diff[rel_path.decode()] = (
            run_in_path(
                ["git", "--no-pager", "diff", dc.from_version, dc.to_version, rel_path],
                dc.working_dir,
            )
            .decode()
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

    return out.stdout


def clone_repo(dc: DiffConfig) -> str:
    """
    Clones the git repository with the given url
    into a temporary folder for the script to execute in.
    """
    # TODO: only clone the needed tags
    subprocess.run(
        ["git", "clone", dc.repo, dc.working_dir], capture_output=True, check=False
    )
