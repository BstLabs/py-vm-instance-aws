from typing import Any, Dict, Generator, Iterator, Tuple

from boto3 import resource
from instances_map_abc.vm_instance_mapping import VmInstanceMappingBase
from instances_map_abc.vm_instance_proxy import VmInstanceProxy

from .ec2_instance_proxy import Ec2InstanceProxy, Ec2RemoteShellProxy


class Ec2AllInstancesData:
    def __init__(self) -> None:
        self._all_instances = resource("ec2").instances.all()
        self._instances_data = [
            (
                _instance.id,
                self._get_instance_name(_instance),
                _instance.state.Code,
                _instance.state.Name,
            )
            for _instance in self._all_instances
        ]

    def __iter__(self) -> Iterator:
        yield from self._instances_data

    def _get_instance_name(self, _instance: Dict[str, Any]) -> str:
        for tag in _instance.tags:
            if tag["Key"] == "Name":
                return tag["Value"]


class Ec2InstanceMapping(VmInstanceMappingBase[VmInstanceProxy]):
    def __init__(self, session) -> None:
        self._session = session
        self._client = self._session.client("ec2")

    def __getitem__(self, name: str) -> VmInstanceProxy:
        instance_id = self._get_instance_id(name)
        return self._get_instance(instance_id)

    def __iter__(self) -> Iterator:
        instances = (
            r["Instances"][0] for r in self._client.describe_instances()["Reservations"]
        )
        for instance in instances:
            yield self._get_instance(instance["InstanceId"])

    def __len__(self) -> int:
        return sum(1 for _ in self)

    def keys(self) -> Generator[str, None, None]:
        for instance in self:
            yield instance.name

    def values(self) -> Generator[str, None, None]:
        yield from self

    def items(self) -> Generator[Tuple[str, str], None, None]:
        yield from zip(self.keys(), self.values())

    def _get_instance(self, instance_id: str) -> Ec2InstanceProxy:
        return Ec2InstanceProxy(instance_id, self._session, ec2_client=self._client)

    def _get_instance_id(self, instance_name: str) -> str:
        """Retrieves instance id, ignores terminated instances."""
        instance_details = self._client.describe_instances(
            Filters=[
                {
                    "Name": "tag:Name",  # as long as you are following the convention of putting Name in tags
                    "Values": [
                        instance_name,
                    ],
                },
                {
                    "Name": "instance-state-name",
                    "Values": [
                        "pending",
                        "running",
                        "shutting-down",
                        "stopping",
                        "stopped",
                    ],
                },
            ],
        )
        if not instance_details["Reservations"]:
            raise RuntimeError(
                "[ERROR] No such instance registered: wrong instance name provided"
            )
        return instance_details["Reservations"][0]["Instances"][0]["InstanceId"]


class Ec2RemoteShellMapping(Ec2InstanceMapping, VmInstanceMappingBase):
    def _get_instance(self, instance_id: str) -> Ec2RemoteShellProxy:
        return Ec2RemoteShellProxy(instance_id, self._session)
