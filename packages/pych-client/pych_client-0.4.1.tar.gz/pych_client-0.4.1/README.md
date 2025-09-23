# pych-client

[![Coverage][coverage-badge]][coverage-url]
[![Tests Status][tests-workflow-badge]][tests-workflow-url]
[![PyPI][pypi-badge]][pypi-url]

pych-client is a [ClickHouse][clickhouse] client for Python built on top of [httpx](https://github.com/encode/httpx/).
It targets the HTTP interface and offers the following features:

- Sync (`ClickHouseClient`) and async (`AsyncClickHouseClient`) clients.
- Streaming requests and responses.
- Load credentials from environment variables, or from a configuration file.

## Installation

```bash
# Default Python JSON parser:
pip install pych-client
# Faster orjson parser:
pip install pych-client[orjson]
```

## Usage

```python
from pych_client import AsyncClickHouseClient, ClickHouseClient

# See "Credential provider chain" for more information on credential specification.
credentials = dict(
    base_url="http://localhost:8123",
    database="default",
    username="default",
    password=""
)

# The client can be used directly, or as a context manager.
# The context manager will ensure that the HTTP client resources
# are properly cleaned-up on exit.
with ClickHouseClient(**credentials) as client:
    # `.bytes()` and `.text()` return the raw response content from the database.
    # `.json()` sets the format to `JSONEachRow` and parse the response content.
    client.bytes("SELECT arrayJoin([1, 2, 3]) AS a")
    # b'1\n2\n3\n'
    client.text("SELECT arrayJoin([1, 2, 3]) AS a")
    # '1\n2\n3\n'
    client.json("SELECT arrayJoin([1, 2, 3]) AS a")
    # [{'a': 1}, {'a': 2}, {'a': 3}]

    # `.iter_bytes()`, `.iter_text()` and `.iter_json()` return the response content
    # as it is received from the database, without buffering the entire response.
    # `.iter_text()` iterates on the line of the response.
    list(client.iter_bytes("SELECT arrayJoin([1, 2, 3]) AS a"))
    # [b'1\n2\n3\n', b'']
    list(client.iter_text("SELECT arrayJoin([1, 2, 3]) AS a"))
    # ['1', '2', '3']
    list(client.iter_json("SELECT arrayJoin([1, 2, 3]) AS a"))
    # [{'a': 1}, {'a': 2}, {'a': 3}]

    # In addition to the query, the following arguments can be set:
    # - `params`: a mapping of query parameters to their values.
    # - `data`: a bytes, string or an interator of bytes to send in the request body.
    # - `settings`: ClickHouse settings (e.g. `{"default_format": "JSONEachRow"`).
    params = {"table": "test_pych"}
    client.text('''
        CREATE TABLE {table:Identifier} (a Int64, b Int64)
        ENGINE MergeTree() ORDER BY (a, b)
    ''', params)
    client.text("INSERT INTO {table:Identifier} VALUES", params, "(1, 2)")
    client.text("INSERT INTO {table:Identifier} VALUES", params, [b"(3, 4)", b"(5, 6)"])
    client.json("SELECT * FROM {table:Identifier} ORDER BY a", params)
    # [{'a': '1', 'b': '2'}, {'a': '3', 'b': '4'}, {'a': '5', 'b': '6'}]

# `AsyncClickHouseClient` offers the same methods:
async with AsyncClickHouseClient(**credentials) as client:
    # Example usage for `.json()` and `.iter_json()`:
    await client.json("SELECT arrayJoin([1, 2, 3]) AS a")
    # [{'a': 1}, {'a': 2}, {'a': 3}]
    async for row in client.iter_json("SELECT arrayJoin([1, 2, 3]) AS a"):
        ...
```

### Command-line interface

```bash
pych-client --help
```

### Credential provider chain

The client looks for credentials in a way similar to the [AWS SDK][aws-sdk]:

1. If one of `base_url`, `database`, `username` or `password` is specified, these values will be used.
2. If none of the previous values are specified, and one of `PYCH_BASE_URL`, `PYCH_DATABASE`, `PYCH_USERNAME`
   or `PYCH_PASSWORD` environment variables are present, these values will be used.
3. If none of the previous values are specified, and the file `~/.config/pych-client/credentials.json` exists, the
   fields `base_url`, `database` and `username` and `password` will be used.
4. If none of the previous values are specified, the values `http://localhost:8213`, `default` and `default`
   will be used.

[aws-sdk]: https://boto3.amazonaws.com/v1/documentation/api/latest/guide/credentials.html

[clickhouse]: https://clickhouse.com

[coverage-badge]: https://img.shields.io/codecov/c/github/dioptra-io/pych-client?logo=codecov&logoColor=white

[coverage-url]: https://codecov.io/gh/dioptra-io/pych-client

[tests-workflow-badge]: https://img.shields.io/github/actions/workflow/status/dioptra-io/pych-client/tests.yml?logo=github&label=tests

[tests-workflow-url]: https://github.com/dioptra-io/pych-client/actions/workflows/tests.yml

[pypi-badge]: https://img.shields.io/pypi/v/pych-client?logo=pypi&logoColor=white

[pypi-url]: https://pypi.org/project/pych-client/
