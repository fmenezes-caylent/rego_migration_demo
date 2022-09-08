from aws_cdk import (
    aws_s3 as s3,
    Stack,
)
import aws_cdk as cdk
from constructs import Construct

class StorageStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, policy_flag, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        if policy_flag:
            s3.Bucket(self, "S3Bucket",
                removal_policy=cdk.RemovalPolicy.DESTROY,
                auto_delete_objects=True)
        else:
            s3.Bucket(self, "S3Bucket")
        
        # s3.Bucket(self, "S3Bucket-2")