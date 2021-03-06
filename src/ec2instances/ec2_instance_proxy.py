import time
from typing import Any, Iterable, Optional, Tuple, Union

import botocore
from boto3 import resource
from instances_map_abc.vm_instance_proxy import VmState


class _Ec2StateProxy(VmState):
    pending = 0
    running = 16
    shutting_down = 32
    terminated = 48
    stopping = 64
    stopped = 80


class Ec2InstanceProxy:
    def __init__(
        self,
        instance_id: str,
        session,
        ec2_client: Optional[botocore.client.BaseClient] = None,
        **kwargs: str,
    ) -> None:
        self._instance_id = instance_id
        self._ec2_client = ec2_client or session.client("ec2")
        self._instance = resource("ec2").Instance(instance_id)

    def start(self, wait: bool = True) -> None:
        """
        Start the vm

        :return: None
        """
        self._ec2_client.start_instances(
            InstanceIds=[self._instance_id],
        )
        wait and self._instance.wait_until_running()  # python short circuiting

    def stop(self, wait: bool = True) -> None:
        """
        Stop the vm

        :return: None
        """
        self._ec2_client.stop_instances(
            InstanceIds=[self._instance_id],
        )
        wait and self._instance.wait_until_stopped()

    @property
    def state(self) -> _Ec2StateProxy:
        return _Ec2StateProxy[self._instance.state["Name"]]

    @property
    def id(self) -> str:
        return self._instance_id

    @property
    def name(self):
        for tag in self._instance.tags:
            if tag["Key"] == "Name":
                return tag["Value"]


class Ec2RemoteShellProxy(Ec2InstanceProxy):
    def __init__(self, instance_id: str, session) -> None:
        super().__init__(instance_id, session)
        self._session = session
        self._ssm_client = self._session.client("ssm")

    def execute(
        self, *commands: Union[str, Iterable], **kwargs: str
    ) -> Union[Tuple[Any, ...], Tuple[str, str]]:
        result = self._ssm_client.send_command(
            InstanceIds=[self._instance_id],
            DocumentName="AWS-RunShellScript",
            Parameters={"commands": ["source /etc/bashrc", *commands]},
        )

        command_id = result["Command"]["CommandId"]
        # see https://stackoverflow.com/questions/50067035/retrieving-command-invocation-in-aws-ssm
        time.sleep(2)
        if not kwargs.get("wait", True):
            return self._ssm_client, command_id, self._instance_id
        waiter = self._ssm_client.get_waiter("command_executed")
        try:
            waiter.wait(
                CommandId=command_id,
                InstanceId=self._instance_id,
                WaiterConfig={
                    "Delay": kwargs.get("delay", 5),
                    "MaxAttempts": kwargs.get("attempts", 20),
                },
            )
        finally:
            result = self._ssm_client.get_command_invocation(
                CommandId=command_id,
                InstanceId=self._instance_id,
                PluginName="aws:RunShellScript",
            )
            print(result.StandardOutputContent)
            print(result.StandardErrorContent)
        return result.StandardOutputContent, result.StandardErrorContent

    @property
    def session(self):
        return self._session
