"""
upgrade-guide-helper | Malte Herrmann | 2024

----

This tool aids in creating upgrade guides between distinct versions of
an evmOS-based blockchain codebase.
"""

import shutil

from git import get_diff_without_imports, DiffConfig


def run():
    """
    The main function to run the tool.
    """
    try:
        diff = get_diff_without_imports(DiffConfig(
            from_version = "v15.0.0",
            to_version = "v16.0.4",
            repo = "https://github.com/evmos/evmos",
        ))
        print(diff)
    finally:
        # # if input("Clean up the temporary working directory? (y/n)\n") == "y":
        print(f"cleaning up {diff.temp_dir}")
        shutil.rmtree(diff.temp_dir)


if __name__ == "__main__":
    run()
