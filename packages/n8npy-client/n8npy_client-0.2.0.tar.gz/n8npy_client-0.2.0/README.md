# n8npy-client

Comprehensive Python wrapper around the [n8n Public REST API](https://docs.n8n.io/api/).
It aims to make it simple to script n8n workflows, manage credentials, inspect
executions, and automate administrative tasks from Python projects, serverless
functions, or CI pipelines.

---

## Table of Contents
1. [Features](#features)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Quick Start](#quick-start)
5. [Endpoint Coverage](#endpoint-coverage)
6. [Usage Examples](#usage-examples)
7. [Pagination & Helpers](#pagination--helpers)
8. [Error Handling](#error-handling)
9. [Development](#development)
10. [Regenerating From OpenAPI](#regenerating-from-openapi)
11. [Packaging & Release](#packaging--release)
12. [Support](#support)

---

## Features
- **Full API surface** – Automatically generated wrappers for every documented
  `/api/v1` endpoint (audit, credentials, executions, projects, source control,
  tags, users, variables, workflows, …).
- **Convenience helpers** – Higher-level methods for common workflow lifecycle
  tasks (pagination, create/update/replace, activate/deactivate) while keeping
  direct access to the raw endpoints.
- **Strong documentation** – Each method exposes a descriptive docstring with
  the HTTP verb, path, arguments, and return contract.
- **Configurable transport** – Centralised HTTP plumbing with consistent
  headers, timeouts, and error messages.
- **Lightweight requirements** – Only depends on `requests` and `python-dotenv`.

---

## Installation
Install from PyPI:

```bash
pip install n8npy-client
```

To work locally with the sources:

```bash
git clone https://github.com/splifter/n8npy
cd n8npy
pip install -e .
```

---

## Configuration
The client reads its configuration from environment variables or a `.env` file.
Only the API key is mandatory.

| Variable        | Description                                               | Default                              |
|-----------------|-----------------------------------------------------------|--------------------------------------|
| `N8N_API_KEY`   | API token for the n8n public API                          | _required_                           |
| `BASE_URL`      | Base URL to the n8n API                                   | `https://n8n.example.com/api/v1`    |

### Example `.env`
```
N8N_API_KEY=pypi-AgE...
BASE_URL=https://your-n8n-instance/api/v1
```

Make sure secrets are excluded from version control (already covered in
`.gitignore`).

---

## Quick Start
```python
from n8n_api import N8nClient

client = N8nClient()
workflows = client.list_workflows(limit=10)
print(f"Fetched {len(workflows)} workflows")

if workflows:
    workflow_id = workflows[0]["id"]
    details = client.get_workflow(workflow_id)
    print(details["name"], workflow_id)
```

---

## Endpoint Coverage
All public endpoints described in the official OpenAPI specification are
represented. Method names follow snake_case versions of the `operationId`.

| Category      | Methods (selection) |
|---------------|---------------------|
| Audit         | `generate_audit` |
| Credentials   | `create_credential`, `get_credential`, `delete_credential`, `transfer_credential` |
| Executions    | `get_executions`, `get_execution`, `delete_execution`, `retry_execution` |
| Projects      | `get_projects`, `create_project`, `add_users_to_project`, `change_user_role_in_project` |
| Tags          | `create_tag`, `get_tags`, `update_tag`, `delete_tag` |
| Users         | `create_user`, `get_users`, `delete_user`, `update_user_role` |
| Variables     | `create_variable`, `get_variables`, `update_variable`, `delete_variable` |
| Workflows     | `create_workflow`, `get_workflows`, `update_workflow`, `replace_workflow`, `transfer_workflow`, `activate_workflow`, `deactivate_workflow` |

Each method is documented inline with its HTTP verb, path, arguments, and
return value expectations.

---

## Usage Examples
### Manage Credentials
```python
from n8n_api import N8nClient

client = N8nClient()
cred = client.create_credential(
    name="GitHub PAT",
    type="githubApi",
    data={"token": "ghp-example"},
)
print("Created", cred["id"])
print(client.get_credential(cred["id"]))
client.delete_credential(cred["id"])
```

### Inspect Executions
```python
executions = client.get_executions(limit=5, includeData=False)
ids = [item["id"] for item in executions.get("data", [])]
print("Recent execution IDs", ids)
if ids:
    details = client.get_execution(ids[0])
    print(details.get("status"))
```

### Workflow Lifecycle
```python
nodes = [
    {
        "id": "Manual Trigger",
        "name": "Manual Trigger",
        "type": "n8n-nodes-base.manualTrigger",
        "typeVersion": 1,
        "position": [260, 300],
        "parameters": {},
    }
]
connections = {}

created = client.create_workflow(
    name="Smoke Test",
    nodes=nodes,
    connections=connections,
    settings={},
)
wid = created["id"]
client.activate_workflow(wid)
client.deactivate_workflow(wid)
client.delete_workflow(wid)
```

### Variables
```python
var = client.create_variable(key="DEPLOY_ENV", value="staging", type="string")
client.update_variable(var["id"], value="production")
client.delete_variable(var["id"])
```

---

## Pagination & Helpers
`list_workflows` transparently walks through `nextCursor` values to return the
complete collection by default. You can set `fetch_all=False` to only retrieve a
single page:

```python
page = client.list_workflows(limit=50, fetch_all=False)
print(len(page))
```

Other endpoints expose raw pagination parameters (`limit`/`cursor`) should you
need manual control.

---

## Error Handling
The internal `_request` helper raises subclasses of `N8nApiError` (`N8nAuthError`,
`N8nNotFoundError`, `N8nRateLimitError`, ...). Each exception carries the HTTP
status code and the parsed response payload so callers can respond precisely.
For example, a 401 response surfaces as:

```
N8nAuthError: GET https://... returned 401: Unauthorized
```

Use standard `try`/`except` blocks to implement retries or custom logging, or
inspect `exc.status_code`/`exc.payload` for programmatic handling.

---

## Development
### Requirements
```bash
pip install .[dev]
```

### Tests
```bash
python -m pytest
```

### Style
- The project targets Python 3.10+.
- The code follows a pragmatic style with type hints and docstrings.
- Keep secrets out of source control.

### Tooling
- Regenerate raw endpoint bindings from OpenAPI:
  ```bash
  python scripts/regen_client.py --write
  ```
- Example automation scripts live in `examples/`.
- CI (GitHub Actions) runs pytest, builds the package, and checks metadata.
---

## Regenerating From OpenAPI
If n8n publishes new API endpoints you can refresh the client bindings with
the helper script:

```bash
python scripts/regen_client.py --write
```

The script downloads the latest OpenAPI document, regenerates the raw endpoint
methods inside `n8n_api.py`, and keeps the convenience helpers intact. Always
run the test-suite afterwards to verify behaviour.
---

## Packaging & Release
1. Update version in `pyproject.toml` (semantic versioning recommended).
2. Build artifacts:
   ```bash
   python -m build
   ```
3. Validate metadata:
   ```bash
   python -m twine check dist/*
   ```
4. Upload to PyPI:
   ```bash
   twine upload dist/*
   ```

*(Remember to export `TWINE_USERNAME=__token__` and `TWINE_PASSWORD` with your
PyPI API token.)*

---

## Support
- **Issues / Bugs**: open an issue in the repository
  [https://github.com/splifter/n8npy](https://github.com/splifter/n8npy).
- **n8n API reference**: [https://docs.n8n.io/api/](https://docs.n8n.io/api/)
- **n8n community**: [https://community.n8n.io/](https://community.n8n.io/)

Happy automating!
