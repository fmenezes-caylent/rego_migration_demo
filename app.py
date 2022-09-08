#!/usr/bin/env python3
import os

import aws_cdk as cdk

from hello_cdk.compute_stack import ComputeStack
from hello_cdk.storage_stack import StorageStack

app = cdk.App()

StorageStack(app, "storage-stack", policy_flag=True)
# ComputeStack(app, "compute-stack")

app.synth()
