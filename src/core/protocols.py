from typing import Protocol, TypeVar

T = TypeVar("T")
T_contra = TypeVar("T_contra", contravariant=True)


class Repository(Protocol[T]):
    def list(self) -> list[T]: ...
    def add(self, event: T) -> None: ...
    def update(self, event: T) -> None: ...


class Publisher(Protocol[T_contra]):
    def publish(self, item: T_contra) -> None: ...
