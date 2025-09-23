# pie-documents

<a href="https://github.com/ArneBinder/pie-core"><img alt="PythonIE" src="https://img.shields.io/badge/-PythonIE-017F2F?style=flat&logo=github&labelColor=gray"></a><br>

[![PyPI](https://img.shields.io/pypi/v/pie-documents.svg)][pypi status]
[![Tests](https://github.com/arnebinder/pie-documents/workflows/Tests/badge.svg)][tests]
[![Codecov](https://codecov.io/gh/arnebinder/pie-documents/branch/main/graph/badge.svg)][codecov]
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]

Annotation-, document- and metric implementations as well as utilities for [Python-IE](https://github.com/ArneBinder/pie-core).

Available annotation types: see [here](src/pie_documents/annotations.py).

Available document types: see [here](src/pie_documents/documents.py).

Available metrics:

- [F1Metric](src/pie_documents/metrics/f1.py)
- [ConfusionMatrix](src/pie_documents/metrics/confusion_matrix.py)
- [SpanLengthCollector](src/pie_documents/metrics/span_length_collector.py)
- [RelationArgumentDistanceCollector](src/pie_documents/metrics/relation_argument_distance_collector.py)
- [SpanCoverageCollector](src/pie_documents/metrics/span_coverage_collector.py)
- [SQuADF1](src/pie_documents/metrics/squad_f1.py)

Document processing utilities:

- [MultiSpanMerger](src/pie_documents/document/processing/merge_multi_spans.py)
- [SpansViaRelationMerger](src/pie_documents/document/processing/merge_spans_via_relation.py)
- [RegexPartitioner](src/pie_documents/document/processing/regex_partitioner.py)
- [RelationArgumentSorter](src/pie_documents/document/processing/relation_argument_sorter.py)
- [SentenceSplitter](src/pie_documents/document/processing/sentence_splitter.py)
- [TextSpanTrimmer](src/pie_documents/document/processing/text_span_trimmer.py)
- [tokenization utils](src/pie_documents/document/processing/tokenization.py), e.g., `text_based_document_to_token_based` and `token_based_document_to_text_based`

## Setup

```bash
pip install pie-documents
```

To install the latest version from GitHub:

```bash
pip install git+https://git@github.com/ArneBinder/pie-documents.git
```

## Development

### Setup

1. This project is build with [Poetry](https://python-poetry.org/). See here for [installation instructions](https://python-poetry.org/docs/#installation).
2. Get the code and switch into the project directory:
   ```bash
   git clone https://github.com/ArneBinder/pie-documents
   cd pie-documents
   ```
3. Create a virtual environment and install the dependencies (including development dependencies):
   ```bash
   poetry install --with dev
   ```

Finally, to run any of the below commands, you need to activate the virtual environment:

```bash
poetry shell
```

Note: You can also run commands in the virtual environment without activating it first: `poetry run <command>`.

### Code Formatting, Linting and Static Type Checking

```bash
pre-commit run -a
```

### Testing

run all tests with coverage:

```bash
pytest --cov --cov-report term-missing
```

### Releasing

1. Create the release branch:
   `git switch --create release main`
2. Increase the version:
   `poetry version <PATCH|MINOR|MAJOR>`,
   e.g. `poetry version patch` for a patch release. If the release contains new features, or breaking changes,
   bump the minor version (this project has no main release yet). If the release contains only bugfixes, bump
   the patch version. See [Semantic Versioning](https://semver.org/) for more information.
3. Commit the changes:
   `git commit --message="release <NEW VERSION>" pyproject.toml`,
   e.g. `git commit --message="release 0.13.0" pyproject.toml`
4. Push the changes to GitHub:
   `git push origin release`
5. Create a PR for that `release` branch on GitHub.
6. Wait until checks passed successfully.
7. Merge the PR into the main branch. This triggers the GitHub Action that creates all relevant release
   artefacts and also uploads them to PyPI.
8. Cleanup: Delete the `release` branch. This is important, because otherwise the next release will fail.

[black]: https://github.com/psf/black
[codecov]: https://app.codecov.io/gh/arnebinder/pie-documents
[pre-commit]: https://github.com/pre-commit/pre-commit
[pypi status]: https://pypi.org/project/pie-documents/
[tests]: https://github.com/arnebinder/pie-documents/actions?workflow=Tests
