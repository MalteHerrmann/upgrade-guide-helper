"""
This module contains the required logic to get the diff between two
git tags in the given repository.
"""

import os
import subprocess
import tempfile
from dataclasses import dataclass
from typing import Dict, List


@dataclass
class DiffConfig:
    """
    Holds the required information of the diff to obtain.
    """

    from_version: str
    to_version: str
    repo: str


class DiffResult:
    """
    Contains the relevant information about the resulting
    diff information.
    """

    def __init__(self, folder: str, diff_output: str):
        self.temp_dir = folder
        self.diff = self.parse_output(diff_output)

    def parse_output(self, out: str) -> Dict[str, List[str]]:
        parsed_diff = {}
        return parsed_diff


def get_diff_without_imports(dc: DiffConfig) -> DiffResult:
    """
    Returns the changed files with corresponding changes
    without those that only adjust import paths between major versions.

    E.g. changes from github.com/evmos/evmos/v16 to github.com/evmos/evmos/v17
    will be ignored.
    """
    result = get_diff(dc)
    for file, changes in result.diff.items():
        print(file, changes)

    return result


def get_diff(dc: DiffConfig) -> DiffResult:
    """
    Returns the changed with corresponding changes
    between the versions to compare.
    """
    tmp_folder = clone_repo(dc.repo)
    print(f"cloned repo into folder {tmp_folder}")

    diff_out = get_diff_in_folder(dc, tmp_folder)

    parsed_diff = DiffResult(tmp_folder, diff_out)
    return parsed_diff


def get_diff_in_folder(dc: DiffConfig, path: str) -> Dict[str, List[str]]:
    """
    Gets the git diff in the given folder.
    """
    out = run_in_path(["git", "--no-pager", "diff", dc.from_version, dc.to_version, "--name-only"], path)
    if not out.stdout:
        return {}

    out_diff = {}
    for rel_path in out.stdout.split():
        out_diff[rel_path] = run_in_path(["git", "--no-pager", "diff", dc.from_version, dc.to_version, rel_path], path) 

    return out_diff


def run_in_path(args: List[str], path: str):
    """
    Executes the command in the given working directory.
    """
    source_dir = os.getcwd()

    os.chdir(path)
    out = subprocess.run(args)
    os.chdir(source_dir)

    return out

def clone_repo(url: str) -> str:
    """
    Clones the git repository with the given url
    into a temporary folder for the script to execute in.
    """
    tmp_folder = tempfile.mkdtemp()

    # TODO: only clone the needed tags
    subprocess.run(["git", "clone", url, tmp_folder])
    return tmp_folder
