import atexit
import threading
import json
from dataclasses import dataclass, field
from typing import Any, cast

from azure.eventhub import EventHubProducerClient, EventDataBatch, EventData
from azure.identity import DefaultAzureCredential


def send_to_eventhub(
    message: dict | str | bytes,
    namespace: str,
    eventhub: str,
    latency: int = 30,
    credential: Any = None,
) -> None:
    BatchHandler.from_namespace(
        namespace,
        eventhub,
        latency=latency,
        credential=credential,
    ).append(message)


_batch_handler_cache = {}


def _cachable_batch_handler_factory(
    namespace: str,
    eventhub: str,
    latency: int = 30,
    credential: Any = None,
) -> "BatchHandler":
    """Internal function to cache BatchHandler object for efficient sending"""
    existing: BatchHandler | None = _batch_handler_cache.get((namespace, eventhub))
    if existing:
        existing.latency = latency
        return existing
    client: EventHubProducerClient = EventHubProducerClient(
        fully_qualified_namespace=namespace,
        eventhub_name=eventhub,
        credential=credential or DefaultAzureCredential(),
    )
    batch: EventDataBatch = client.create_batch()
    handler = BatchHandler(
        client=client,
        batch=batch,
        latency=latency,
    )
    _batch_handler_cache[(namespace, eventhub)] = handler
    return handler


@dataclass
class BatchHandler:
    """
    Class to handle appending to, and building up of batches for efficient event
    hub use.

    Note: Uses threading locks to avoid race conditions, which will *only* hold
    if called using threading executors rather than asyncio.
    """

    client: EventHubProducerClient
    batch: EventDataBatch
    latency: int
    _lock: threading.Lock = field(default_factory=threading.Lock)
    _waiting: bool = False
    _errors: list[type[Exception]] = field(default_factory=list)

    @classmethod
    def from_namespace(
        cls,
        namespace: str,
        eventhub: str,
        latency: int = 30,
        credential: Any = None,
    ) -> "BatchHandler":
        """
        Class method to create a batch handler object from a given azure namespace
        and eventhub.
        """
        return _cachable_batch_handler_factory(
            namespace=namespace,
            eventhub=eventhub,
            latency=latency,
            credential=credential,
        )

    def _raise_background_errors(self) -> None:
        """
        Because send and flush happens in a timer thread, background exception won't
        be passed up the stack. This raises the error in the main thread so that
        they can be handled.
        """
        previous_errors: list[type[Exception]] = self._errors
        if len(previous_errors) > 0:
            self._errors = []
            raise previous_errors[0]

    def _send_and_flush(self) -> None:
        """
        Send batch, and replace with new empty batch
        """
        with self._lock:
            if self.batch.size_in_bytes <= 0:
                return
            try:  # pragma: no cover
                with self.client:
                    self.client.send_batch(self.batch)
                self.batch = self.client.create_batch()
            except Exception as error:  # pragma: no cover
                print(error)
                self._errors.append(error)
                raise error
            finally:  # pragma: no cover
                self._waiting = False

    def append(self, msg: str | bytes | dict) -> None:
        """
        Append a message onto the batch, sending only if necessary to make space.
        """
        self._raise_background_errors()
        safe_msg: str | bytes = cast(
            str | bytes,
            json.dumps(msg) if isinstance(msg, dict) else msg,
        )
        with self._lock:
            try:
                self.batch.add(EventData(safe_msg))
            except ValueError:  # pragma: no cover
                # batch is full
                self._send_and_flush()
                self.batch.add(EventData(safe_msg))
            if not self._waiting:
                self._timer = threading.Timer(self.latency, self._send_and_flush)
                self._timer.daemon = True
                self._timer.start()
                self._waiting = True

    def __post_init__(self) -> None:
        """Register self and flush to exit of program to avoid unsent messages"""
        atexit.register(self._send_and_flush)
