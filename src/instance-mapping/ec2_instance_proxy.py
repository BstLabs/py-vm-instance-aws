from enum import auto
from typing import Tuple

from vm_instance_proxy import VmState


class _Ec2State(VmState):
    UNKNOWN = auto()  # this is the only value not taken from AWS instance states
    PENDING = auto()
    RUNNING = auto()
    STOPPING = auto()
    STOPPED = auto()
    SHUTTING_DOWN = auto()
    TERMINATED = auto()


class Ec2InstanceProxy:
    def __init__(self, name) -> None:
        self._name = name
        self._state = _Ec2State.UNKNOWN

    async def start(self, trace: bool) -> None:
        ...  # TODO implement

    async def stop(self, trace: bool) -> None:
        ...  # TODO implement

    async def reboot(self, trace: bool) -> None:
        ...  # TODO implement

    @property
    def state(self) -> _Ec2State:  # TODO use the enum
        return self._state


class Ec2RemoteShellProxy(Ec2InstanceProxy):
    def __init__(self, name) -> None:
        ...  # TODO implement

    async def execute(self, *commands: str) -> Tuple[str, str]:
        ...  # TODO implement
