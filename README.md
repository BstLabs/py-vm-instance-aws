# AWS Instance Mapping library

This library is intended to help using AWS EC2 instances in a more developer friendly manner.

[ec2map](https://github.com/BstLabs/py-vm-instance-aws) was developed by [BST LABS](https://github.com/BstLabs/) as an open source generic infrastructure foundation for the cloud version of Python run-time within the scope of the [Cloud AI Operating System (CAIOS)](http://caios.io) project.

## Installation

To use it in your projects you need to install it via `pip3`

```bash
pip3 install ec2map
```

## Usage

```python
from ec2instances.ec2_instance_mapping import Ec2RemoteShellMapping
from ec2instances.ec2_instance_proxy import Ec2InstanceProxy, Ec2RemoteShellProxy
```

## License

MIT License, Copyright (c) 2021-2022 BST LABS. See [LICENSE](https://github.com/BstLabs/py-vm-instance-aws/LICENSE.md) file.
