import uuid

from httpx import AsyncClient

PATH = "/search"


async def test_trace_id_is_generated_when_header_is_missing(
    client: AsyncClient,
) -> None:
    response = await client.get(PATH)

    uuid.UUID(response.headers["x-trace-id"])


async def test_incoming_trace_id_is_reused(client: AsyncClient) -> None:
    response = await client.get(PATH, headers={"X-Trace-Id": "some-fixed-id"})

    assert response.headers["x-trace-id"] == "some-fixed-id"


async def test_generated_trace_ids_are_unique(client: AsyncClient) -> None:
    first = await client.get(PATH)
    second = await client.get(PATH)

    assert first.headers["x-trace-id"] != second.headers["x-trace-id"]
