from types import FunctionType
from typing import Any, Callable, Optional, Tuple, Union

import botocore
from boto3 import resource
from botocore.exceptions import ClientError
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
        auth_callback: Optional[Callable] = None,
        **kwargs: str,
    ) -> None:
        try:
            self._instance_id = instance_id
            self._ec2_client = ec2_client or session.client("ec2")
            self._instance = resource("ec2").Instance(instance_id)
            self._instance.state  # TODO this line raises the exception (in case of credentials problem)
        except ClientError:
            if isinstance(auth_callback, FunctionType):
                auth_callback(**kwargs)
            else:
                raise

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

    def wait_until_running(self) -> None:
        """
        Waiter for running state

        :return: None
        """
        if self.state == _Ec2StateProxy.pending:
            self._instance.wait_until_running()

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
    def __init__(
        self, instance_id: str, session, auth_callback: Optional[Callable] = None
    ) -> None:
        super().__init__(instance_id, session, auth_callback=auth_callback)
        self._session = session
        self._ssm_client = self._session.client("ssm")

    def execute(
        self,
        *command: str,
        delay: int = 1,
        attempts: int = 60,
        wait: bool = True,
        **parameters: str,
    ) -> Union[Tuple[Any, ...], str]:

        try:
            assert self.state.name == "running"
        except AssertionError as assert_err:
            raise RuntimeError(
                f"instance {self._instance_id} is not in a valid state"
            ) from assert_err

        result = self._ssm_client.send_command(
            InstanceIds=[self._instance_id],
            DocumentName="AWS-RunShellScript",
            Parameters={"commands": ["source /etc/bashrc", *command], **parameters},
        )

        command_id = result["Command"]["CommandId"]
        if not wait:
            return command_id

        waiter = self._ssm_client.get_waiter("command_executed")
        waiter.wait(
            CommandId=command_id,
            InstanceId=self._instance_id,
            WaiterConfig={"Delay": delay, "MaxAttempts": attempts},
        )

        response = self._ssm_client.get_command_invocation(
            CommandId=command_id,
            InstanceId=self._instance_id,
            PluginName="aws:RunShellScript",
        )

        return (
            response["StandardOutputContent"].rstrip("\n"),
            response["StandardErrorContent"].rstrip("\n"),
        )

    @property
    def session(self):
        return self._session
