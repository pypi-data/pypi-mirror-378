from typing import Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from azure.eventhub import EventHubConsumerClient, PartitionContext, EventData
from zoneinfo import ZoneInfo
from azure.identity import DefaultAzureCredential
from flex.stream import send_to_eventhub
from datetime import datetime


class Status(Enum):
    SUCCESS = "SUCCESS"
    FAIL = "FAIL"
    INFO = "INFO"


_STATUSTIMEFORMAT = "%Y-%m-%dT%H:%M:%S%z"


@dataclass
class StatusMessage:
    name: str
    status: Status
    timestamp: datetime = field(default_factory=lambda: datetime.now(ZoneInfo("UTC")))
    info: dict = field(default_factory=dict)

    def to_dict(self) -> dict[str, str]:
        return {
            "name": self.name,
            "status": self.status.value,
            "timestamp": self.timestamp.strftime(_STATUSTIMEFORMAT),
            "info": self.info,
        }

    def log(self, namespace, eventhub, latency=0, credential=None) -> None:
        send_to_eventhub(
            self.to_dict(),
            namespace,
            eventhub,
            latency=latency,
            credential=credential,
        )


@dataclass
class TaskReciever:
    """
    This class can be used for responding to StatusMessage type events on an
    eventhub. It's recommended to be intialised with the `from_namespace` class
    method rather than directly.

    The following code initialises a TaskReciever object, and prints out any messages
    that are of the type SUCCESS and with the name 'a-nice-message':

    ```python
    from flex.stream import task_logging

    reciever = task_logging.TaskReciever.from_namespace(
        "namespace.servicebus.windows.net",
        "eventhubname",
        consumer_group="$Default",
        name_filter="a-nice-message",
        status_filter=task_logging.Status.SUCCESS,
    )
    with reciever:
        reciever.listen(print)
    ```

    Here "print" is attached to the listen function, but any callable which
    takes a `task_logging.StatusMessage` can be attached.

    Some important notes on the above code is that it's *blocking* and will
    continually listen for events until interupted (so will likely need to run
    in a distinct thread if your application is doing other tasks alongside
    listening to events).

    It's also worth understanding "consumer_group" - Azure event hubs require
    a single distinct consumer_group in order to recieve events, you *won't* be
    able to use the same consumer_group twice at the same time, so will need
    a consumer_group set up for your distinct application that is listening.
    """

    consumer_client: EventHubConsumerClient
    name_filter: str | None = None
    status_filter: Status | None = None

    @classmethod
    def from_namespace(
        cls,
        namespace: str,
        eventhub: str,
        consumer_group: str,
        name_filter: str | None = None,
        status_filter: Status | None = None,
        credential: Any = None,
    ) -> "TaskReciever":
        credential = credential or DefaultAzureCredential()
        return TaskReciever(
            consumer_client=EventHubConsumerClient(
                fully_qualified_namespace=namespace,
                eventhub_name=eventhub,
                credential=credential,
                consumer_group=consumer_group,
            ),
            name_filter=name_filter,
            status_filter=status_filter,
        )

    def __enter__(self) -> "TaskReciever":
        return self

    def __exit__(self, *args: Any) -> None:
        self.consumer_client.close()

    def _recieve_wrapper(
        self,
        on_event: Callable[[StatusMessage], Any],
    ) -> Callable[[PartitionContext, EventData], Any]:  # pragma: no cover
        def new_on_event(
            partition_context: PartitionContext, event_data: EventData
        ) -> Any:
            data = event_data.body_as_json()
            status_message = StatusMessage(
                name=data["name"],
                status=Status[data["status"].upper()],
                timestamp=datetime.strptime(data["timestamp"], _STATUSTIMEFORMAT),
                info=data["info"],
            )
            if self.name_filter and status_message.name != self.name_filter:
                return
            if self.status_filter and status_message.status != self.status_filter:
                return
            return on_event(status_message)

        return new_on_event

    def listen(
        self, on_event: Callable[[StatusMessage], Any]
    ) -> None:  # pragma: no cover
        return self.consumer_client.receive(on_event=self._recieve_wrapper(on_event))
