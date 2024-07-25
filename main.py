"""
upgrade-guide-helper | Malte Herrmann | 2024

----

This tool aids in creating upgrade guides between distinct versions of
an evmOS-based blockchain codebase.
"""

import tempfile
import sys
from getopt import gnu_getopt
from shutil import rmtree

from models import AVAILABLE_MODELS, summarize
from git import get_filtered_diff, DiffConfig


def run(model: str, from_version: str, to_version: str):
    """
    The main function to run the tool.

    Takes in two version tags of the repository to compare.
    """
    dc = DiffConfig(
        llm=model,
        from_version=from_version,
        to_version=to_version,
        repo="https://github.com/evmos/evmos",
        working_dir=tempfile.mkdtemp(),
    )

    try:
        diff = get_filtered_diff(dc)
    finally:
        print(f"cleaning up {dc.working_dir}")
        rmtree(dc.working_dir)

    summary = summarize(dc.llm, diff)
    print(summary)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 main.py FROM_VERSION TO_VERSION")
        sys.exit()

    model = "gpt-4o-mini"
    optlist, args = gnu_getopt(sys.argv[3:], "m", ["model"])
    for opt, arg in zip(optlist, args):
        if opt[0] in ["-m", "--model"]:
            model = arg
            continue

        raise ValueError(f"unknown flag: '{opt[0]}'")

    if model not in AVAILABLE_MODELS:
        raise ValueError(
            f"invalid model: {model}; available models: {AVAILABLE_MODELS}"
        )

    from_version, to_version = sys.argv[1], sys.argv[2]

    run(model, from_version, to_version)
