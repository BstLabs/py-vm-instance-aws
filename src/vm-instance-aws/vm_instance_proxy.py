from enum import Enum
from typing import Protocol, Tuple


class VmState(Enum):
    ...


class VmInstanceProxy(Protocol):
    def start(self, wait: bool = True) -> None: ...
    def stop(self, wait: bool = True) -> None: ...

    @property
    def state(self) -> VmState: ...


class RemoteShellProxy(VmInstanceProxy):
    def execute(self, *commands: str) -> Tuple[str, str]: ...
