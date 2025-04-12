from typing import Protocol, TypeVar

T = TypeVar("T")

class Repository(Protocol[T]):
    def list(self) -> list[T]: ...
    def add(self, event: T) -> None: ...
    def update(self, event_id: str, event: T) -> None: ...


class Publisher(Protocol[T]):
    def publish(self, item: T) -> None: ...
