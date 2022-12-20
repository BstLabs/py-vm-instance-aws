import os
import sys
import warnings
from unittest import TestCase, main

import boto3

from src.ec2instances.ec2_instance_proxy import Ec2RemoteShellProxy


class TestRemoteShell(TestCase):
    @classmethod
    def setUpClass(cls):
        warnings.filterwarnings(
            action="ignore", message="unclosed", category=ResourceWarning
        )
        try:
            cls._instance_id = os.environ["EC2MAP_TEST_INSTANCE_ID"]
        except KeyError:
            print("Expected env var EC2MAP_TEST_INSTANCE_ID")
            sys.exit(1)

    def test_remote_shell(self):
        shell = Ec2RemoteShellProxy(
            instance_id=self._instance_id,
            session=boto3.Session(),
        )
        out, err = shell.execute(os.environ.get("EC2MAP_TEST_COMMAND", "echo ~"))
        print()
        print("out:", out)
        print("err:", err)


if __name__ == "__main__":
    main()
