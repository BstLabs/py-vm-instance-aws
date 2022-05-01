from typing import Iterator

from boto3 import Session  

from ec2_instance_proxy import Ec2InstanceProxy, Ec2RemoteShellProxy
from vm_instance_mapping import VmInstanceMappingBase
from vm_instance_proxy import VmInstanceProxy


class Ec2InstanceMapping(VmInstanceMappingBase[VmInstanceProxy]):
    def __init__(self) -> None:
        self._client = Session().client("ec2")

    def __getitem__(self, name: str) -> VmInstanceProxy:
        instance_id = self._get_instance_id(name)
        return self._get_instance(instance_id)

    def __iter__(self) -> Iterator:
        yield from self._client.describe_instances()["Reservations"]

    def __len__(self) -> int:
        return sum(1 for _ in self)

    def _get_instance(self, id: str) -> Ec2InstanceProxy:
        return Ec2InstanceProxy(id)

    def _get_instance_id(self, instance_name: str) -> str:
        instance_details = self._client.describe_instances(
            Filters=[
                {
                    'Name': 'tag:Name',  # as long as you are following the convention of putting Name in tags
                    'Values': [
                        instance_name,
                    ]
                },
            ],
        )
        return instance_details["Reservations"][0]["Instances"][0]["InstanceId"]


class Ec2RemoteShellMapping(Ec2InstanceMapping, VmInstanceMappingBase):
    def _get_instance(self, id: str) -> Ec2RemoteShellProxy:
        return Ec2RemoteShellProxy(id)
