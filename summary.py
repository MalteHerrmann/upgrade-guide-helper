"""
Contains the required logic to call the LLM
to request a summary of the provided changes
between two versions.
"""

import os
from typing import Dict
from openai import OpenAI

from git import DiffResult


REL_PATH_APP = "app/app.go"
REL_PATH_GO_MOD = "go.mod"
REL_PATH_UPGRADES = "app/upgrades"
APP_CHANGE_PROMPT = """
You are a code change analyzer, specialized in providing a
summary of the made changes in a Git diff output.
The code base is based on Evmos, a Cosmos SDK-based blockchain
that offers an EVM implementation, so please consider
the native elements of this framework when deriving and
providing the summary of the changes in the main application
wiring.

Specifically, pay attention to changes to the code structure
or additions of modules or module keepers.
"""
GO_MOD_PROMPT = """
You are a code change analyzer, specialized in providing a concise
summary of changes introduced to a Go module file.
The provided input will be the Git diff output between
the go.mod files of two compared versions.

The target codebase is Evmos, a Cosmos SDK-based blockchain that
offers an EVM implementation.

Please make sure to only stick to version changes of the most important
dependencies: Cosmos SDK, IBC-Go and Go-Ethereum.
Please also mind the replace directives for Evmos' own forks.
If there are no changes to the listed main dependencies, please provide no output.
"""
UPGRADE_CHANGE_PROMPT = """
You are a code change analyzer, specialized in providing
a written summary of the made changes in a series of
Git diff outputs.

These outputs describe the changes between two versions of Evmos,
a Cosmos SDK-based blockchain that offers an EVM implementation,
which means that the upgrade logic in the given changes relate to
a chain upgrade of the underlying blockchain.

Please provide a concise summary of the upgrade logic
at hand. Usually this will include parameter adjustments,
data migrations or the introduction or removal of modules.
"""


def summarize(diff: DiffResult) -> None:
    """
    Runs the full logic to summarize the changes between
    two versions.
    """
    app_changes = None
    upgrades_changes = {}
    deps_changes = None

    for file, changes in diff.diff.items():
        joint_changes = "\n".join(changes)
        if file == REL_PATH_APP:
            app_changes = joint_changes
        elif REL_PATH_UPGRADES in file:
            upgrades_changes[file] = joint_changes
        elif REL_PATH_GO_MOD == file:
            deps_changes = joint_changes

    if deps_changes:
        answer = call_llm(GO_MOD_PROMPT, deps_changes)
        print(answer)

    if app_changes:
        answer = call_llm(APP_CHANGE_PROMPT, app_changes)
        print(answer)

    if upgrades_changes:
        answer = summarize_upgrade_changes(upgrades_changes)
        print(answer)


def summarize_upgrade_changes(changes: Dict[str, str]) -> str:
    """
    Prepares the upgrade changes prompt and calls the LLM.
    """
    upgrade_changes = []
    for file, change in changes.items():
        upgrade_changes.append(f"{file}:\n{change}")

    upgrade_string = "\n".join(upgrade_changes)
    return call_llm(UPGRADE_CHANGE_PROMPT, upgrade_string)


def call_llm(context: str, user_prompt: str) -> str:
    """
    Calls the OpenAI API with the given context and user prompts.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key or "sk-" not in api_key[:3]:
        raise ValueError("OpenAI API key not found")

    client = OpenAI(
        api_key=api_key,
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": context,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
        model="gpt-4o-mini",
    )

    return chat_completion.choices[0].message.content
