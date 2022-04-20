from typing import Iterator

from ec2_instance_proxy import Ec2InstanceProxy, Ec2RemoteShellProxy
from vm_instance_mapping import VmInstanceMappingBase
from vm_instance_proxy import VmInstanceProxy


class Ec2InstanceMapping(VmInstanceMappingBase[VmInstanceProxy]):
    def __getitem__(self, name) -> VmInstanceProxy:
        return self.get_instance(name)

    def __iter__(self) -> Iterator:
        ...  # TODO implement

    def __len__(str) -> int:
        ...  # TODO implement

    def get_instance(self, name) -> Ec2InstanceProxy:
        return Ec2InstanceProxy(name)


class Ec2RemoteShellMapping(Ec2InstanceMapping, VmInstanceMappingBase):
    def get_instance(self, name) -> Ec2RemoteShellProxy:
        return Ec2RemoteShellProxy(name)
