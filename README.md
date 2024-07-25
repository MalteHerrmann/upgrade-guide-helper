# Upgrade Guide Helper

This tool scans the Git repository of an evmOS-based blockchain
for changes between two versions, that affect the required upgrade logic.

## Usage

To compare two Git tags in the evmOS repository and produce a summary
using one of the [available models](./models/models.py), run:

```shell
pip3 install requirements.txt
python3 main.py FROM_VERSION TO_VERSION [FLAGS]
```

An example, that is specifying `gpt-4o` to be used for the comparison
of v17.0.0 and v18.0.0, would be:

```shell
python3 main.py v17.0.0 v18.0.0 -m gpt-4o
```

This will write the summary into a Markdown file within the `summaries/` subdirectory.
