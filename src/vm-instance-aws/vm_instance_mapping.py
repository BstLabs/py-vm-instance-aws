from collections.abc import Mapping
from typing import Iterator, TypeVar

from vm_instance_proxy import RemoteShellProxy, VmInstanceProxy

I = TypeVar("I", VmInstanceProxy, RemoteShellProxy)


class VmInstanceMappingBase(Mapping[str, I]):
    def __getitem__(self, name: str) -> I: ...
    def __iter__(self) -> Iterator: ...
    def __len__(str) -> int: ...
