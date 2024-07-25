"""
Contains the required logic to call the LLM
to request a summary of the provided changes
between two versions.
"""

import os
from json import dumps
from anthropic import Anthropic
from openai import OpenAI

from git import DiffResult
from .models import ANTHROPIC_MODELS, GPT_MODELS


CHANGES_LINES_LIMIT = 5_000
REL_PATH_APP = "app/app.go"
REL_PATH_GO_MOD = "go.mod"
REL_PATH_UPGRADES = "app/upgrades"
CONTEXT_PROMPT = """
You are a code change analyzer, specialized in providing a
summary of the made changes in a Git diff output.
The code base is based on Evmos, a Cosmos SDK-based blockchain
that offers an EVM implementation, so please consider
the native elements of this framework when deriving and
providing the summary of the changes in the main application
wiring.

There are other chains building on top of the Evmos codebase,
which should be provided with guides for the necessary changes,
that they need to make to their codebases, to upgrade their chains
accordingly when bumping the version of Evmos that they are using
as a dependency.

You will be presented with a JSON structure, containing Git diff outputs
for the different relevant files between two major versions of
the Evmos codebase.

The changes in the go.mod file should be scanned for version adjustments
and/or changes to Evmos' main dependencies, which are Cosmos SDK, IBC-Go
and Go-Ethereum. Please also be mindful of changes to the replace directives
of the corresponding forks. Do not mention changes in other dependencies as
they are not relevant.

The changes in the app/app.go file are critical as they reflect the wiring
of the main application. Please provide a clean summary of things adjusted in this
file including the corresponding new lines in form of code blocks, which are
to be shared with customers. Common changes here include additions or removals of methods,
that include module keepers and other related store entries.
When the Cosmos SDK dependency is upgraded in go.mod, it is also common for the app.go file
to include more drastic changes as a result of the underlying dependency changing.

The changes in Go files with a path of app/upgrades/... define the necessary upgrade logic
for the chain to run. This will usually include parameter adjustments,
data migrations or the addition/removal of individual modules.

For all the listed Go files to analyze, you do not need to mention any changes in
module imports in the given files, just focus on the logic changes.

Please provide a summary in Markdown format, that is grouped for these three categories:
- dependency upgrades
- application wiring
- upgrade logic.
"""


def summarize(model, diff: DiffResult) -> str:
    """
    Runs the full logic to summarize the changes between
    two versions.
    """
    changes_to_summarize = {}

    for file, changes in diff.diff.items():
        joint_changes = "\n".join(changes)
        if file in [REL_PATH_APP, REL_PATH_GO_MOD] or REL_PATH_UPGRADES in file:
            changes_to_summarize[file] = joint_changes

    if not changes_to_summarize:
        raise ValueError("found no changes to summarize")

    return call_llm(model, CONTEXT_PROMPT, dumps(changes_to_summarize))


def call_llm(model, context: str, user_prompt: str) -> str:
    """
    Calls the OpenAI API with the given context and user prompts.
    """
    if model in GPT_MODELS:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key or "sk-" not in api_key[:3]:
            raise ValueError("OpenAI API key not found")

        client = OpenAI(
            api_key=api_key,
        )

        answer = (
            client.chat.completions.create(
                model=model,
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
            )
            .choices[0]
            .message.content
        )

    elif model in ANTHROPIC_MODELS:
        anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
        client = Anthropic(api_key=anthropic_key)

        answer = (
            client.messages.create(
                model=model,
                max_tokens=4096,
                system=context,
                messages=[
                    {
                        "role": "user",
                        "content": user_prompt,
                    },
                ],
            )
            .content[0]
            .text
        )

    else:
        raise ValueError(f"{model} not supported")

    return answer
