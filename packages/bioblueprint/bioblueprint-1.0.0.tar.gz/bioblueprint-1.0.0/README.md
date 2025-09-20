# BioBlueprint

BioBlueprint is a python library designed to enable workflow language-interchangeable dependency graph compilation and development automation. It operates by compiling workflows, their dependencies, Git diff between branches, and using the modified files to trace testing paths within the dependency graph.

<br>

## Usage

Please see the help menu for a comprehensive list of input options.

`bioblueprint -i <REPO_BASE_DIR> -db <DEVELOPMENT_BRANCH>`

**DEVELOPMENT**: `-db` is the dev branch; `-sb` is `main` (default)

**VALIDATION**: `-db` is `main`; `-sb` is the previous release tag

<br>

## Outputs

An output directory `bioblueprint_YYYYmmdd/` will be generated containing the following files:

### `<REPO>.pr.md`

A populated pull request template with I/O modifications, WF modifications, and testing paths. If `-pr` is specified, the PR will be downloaded and relevant fields populated with I/O and testing information - existing testing data will be retained and unmodified if formatted as a checklist with exact workflow name matches that are the first entry following the markdown checkbox (links are permitted). This function is tailored for accounted repositories:

- [Public Health Bioinformatics](https://github.com/theiagen/public_health_bioinformatics)

### `<REPO>_inputs.tsv` & `<REPO>_outputs.tsv`

Updated inputs/outputs tables for Public Health Bioinformatics

### `<REPO>.io.json`

A JSON formatted to convey inputs and outputs, including defaults and types, for workflows:

```json
{
  <WF_NAME_1>: {
    "path": <PATH_RELATIVE_TO_REPO>,
    "inputs": {
        <INPUT_1>:
        {
            "type": <WF_LANGUAGE_TYPE>,
            "default": <DEFAULT_VAL>
        },
        ..
    },
    "outputs": {
        <OUTPUT_1>: <WF_LANGUAGE_TYPE>,
        ..
    }
  },
  ..
}
```

### `<REPO>.testing.json`

A JSON formatted to convey affected workflows and the causal dependencies:

```json
{
  <WF_NAME_1>: {
    "path": <PATH_RELATIVE_TO_REPO>,
    "modifications": [
        <TASK/WF_1>,
        ..
    ]
  },
  ..
}
```