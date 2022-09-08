from aws_cdk import (
    aws_autoscaling as autoscaling,
    aws_ec2 as ec2,
    aws_elasticloadbalancingv2 as elbv2,
    App, CfnOutput, Stack,
    aws_s3 as s3,
)
import aws_cdk as cdk

from constructs import Construct

class HelloCdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, flag, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        bucket = s3.Bucket(self, "MyFirstBucket", versioned=True,
            # removal_policy=cdk.RemovalPolicy.DESTROY,
            # auto_delete_objects=True
        )

        # vpc = ec2.Vpc(self, "VPC")
       
        # if flag:
        #     lb = elbv2.ApplicationLoadBalancer(
        #         self, "LB",
        #         vpc=vpc,
        #         internet_facing=True)

        #     asg = autoscaling.AutoScalingGroup(
        #         self,
        #         "ASG",
        #         vpc=vpc,
        #         instance_type=ec2.InstanceType.of(
        #             ec2.InstanceClass.BURSTABLE2, ec2.InstanceSize.MICRO
        #         ),
        #         machine_image=ec2.AmazonLinuxImage(generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2),
        #     )

        #     listener = lb.add_listener("Listener", port=80)
        #     listener.add_targets("Target", port=80, targets=[asg])
        #     listener.connections.allow_default_port_from_any_ipv4("Open to the world")

        #     asg.scale_on_request_count("AModestLoad", target_requests_per_minute=60)
        #     CfnOutput(self,"LoadBalancer",export_name="LoadBalancer",value=lb.load_balancer_dns_name)



        
