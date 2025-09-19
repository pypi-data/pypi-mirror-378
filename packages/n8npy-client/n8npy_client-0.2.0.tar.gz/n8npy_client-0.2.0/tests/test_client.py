import logging
from typing import Iterator

import pytest
import responses

from n8n_api import (
    N8nAuthError,
    N8nClient,
    N8nNotFoundError,
)


@responses.activate
def test_get_workflow_not_found_raises_custom_error() -> None:
    responses.add(
        method=responses.GET,
        url="https://example.test/api/v1/workflows/123",
        json={"message": "Workflow not found"},
        status=404,
    )
    client = N8nClient(base_url="https://example.test/api/v1", api_key="token", logger=logging.getLogger("test"))

    with pytest.raises(N8nNotFoundError) as exc:
        client.get_workflow("123")

    assert exc.value.status_code == 404
    assert exc.value.payload["message"] == "Workflow not found"


def test_headers_without_api_key_fails() -> None:
    client = N8nClient(base_url="https://example.test/api/v1", api_key="")

    with pytest.raises(N8nAuthError):
        client.list_workflows(fetch_all=False)


def test_list_workflows_collector(monkeypatch: pytest.MonkeyPatch) -> None:
    pages: Iterator[dict] = iter(
        [
            {"data": [{"id": "1", "name": "First"}], "nextCursor": "abc"},
            {"data": [{"id": "2", "name": "Second"}, {"id": "3", "name": "Third"}], "nextCursor": None},
        ]
    )

    client = N8nClient(base_url="https://example.test/api/v1", api_key="token")

    def fake_get_workflows(**kwargs):  # type: ignore[override]
        return next(pages)

    monkeypatch.setattr(client, "get_workflows", fake_get_workflows)

    items = client.list_workflows(fetch_all=True)

    assert [item["id"] for item in items] == ["1", "2", "3"]
