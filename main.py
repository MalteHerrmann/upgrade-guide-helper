"""
upgrade-guide-helper | Malte Herrmann | 2024

----

This tool aids in creating upgrade guides between distinct versions of
an evmOS-based blockchain codebase.
"""

import tempfile
from shutil import rmtree

from models import Models, summarize
from git import get_filtered_diff, DiffConfig


def run():
    """
    The main function to run the tool.
    """
    dc = DiffConfig(
        llm=Models.SONNET,
        from_version="v15.0.0",
        to_version="v16.0.4",
        repo="https://github.com/evmos/evmos",
        working_dir=tempfile.mkdtemp(),
    )

    try:
        diff = get_filtered_diff(dc)
    finally:
        print(f"cleaning up {dc.working_dir}")
        rmtree(dc.working_dir)

    summarize(dc.llm, diff)


if __name__ == "__main__":
    run()
