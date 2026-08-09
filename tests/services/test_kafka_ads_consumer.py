import typing
from dataclasses import dataclass, field

from src.application.ports.usecases import IndexAdPort, RemoveAdPort
from src.application.services.kafka_ads_consumer import KafkaAdsConsumer
from src.trace import get_trace_id


@dataclass
class FakeMessage:
    value: dict[str, typing.Any]
    headers: list[tuple[str, bytes]] = field(default_factory=list)


class FakeConsumer:
    def __init__(self, messages: list[FakeMessage]) -> None:
        self._messages = messages
        self.commits = 0

    def __aiter__(self) -> typing.AsyncIterator[FakeMessage]:
        return self._iterate()

    async def _iterate(self) -> typing.AsyncIterator[FakeMessage]:
        for message in self._messages:
            yield message

    async def commit(self) -> None:
        self.commits += 1


class RecordingIndexAd(IndexAdPort):
    def __init__(self) -> None:
        self.trace_ids: list[str] = []

    async def execute(self, ad_id: int) -> None:
        self.trace_ids.append(get_trace_id())


class RecordingRemoveAd(RemoveAdPort):
    def __init__(self) -> None:
        self.trace_ids: list[str] = []

    async def execute(self, ad_id: int) -> None:
        self.trace_ids.append(get_trace_id())


def created(ad_id: int) -> dict[str, typing.Any]:
    return {"event": "ad.created", "payload": {"ad_id": ad_id}}


async def test_consumer_uses_trace_id_from_headers() -> None:
    index_ad = RecordingIndexAd()
    consumer = FakeConsumer([FakeMessage(created(1), [("x-trace-id", b"abc")])])

    await KafkaAdsConsumer(
        consumer=consumer,
        index_ad=index_ad,
        remove_ad=RecordingRemoveAd(),
    ).run()

    assert index_ad.trace_ids == ["abc"]
    assert consumer.commits == 1


async def test_consumer_does_not_inherit_previous_trace_id() -> None:
    index_ad = RecordingIndexAd()
    consumer = FakeConsumer(
        [
            FakeMessage(created(1), [("x-trace-id", b"abc")]),
            FakeMessage(created(2)),
        ]
    )

    await KafkaAdsConsumer(
        consumer=consumer,
        index_ad=index_ad,
        remove_ad=RecordingRemoveAd(),
    ).run()

    first, second = index_ad.trace_ids
    assert first == "abc"
    assert second and second != "abc"


async def test_consumer_clears_trace_id_after_message() -> None:
    consumer = FakeConsumer([FakeMessage(created(1), [("x-trace-id", b"abc")])])

    await KafkaAdsConsumer(
        consumer=consumer,
        index_ad=RecordingIndexAd(),
        remove_ad=RecordingRemoveAd(),
    ).run()

    assert get_trace_id() == ""
