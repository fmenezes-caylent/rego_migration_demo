# Checking out CDK's logging using `cdk synth` and `cdk diff`

Before using this tutorial, follow instructions on [README.md](/README.md) file to setup your environment.

Our goal is to be able to to see changes in stacks prior to deploying them to testing and production environments. Therefore, we will create a simple stack, comprised of an S3 bucket, VPC, Autoscaling group, Load Balancer and a CFN Output.

This guide is divided into 3 steps. First, we will deploy a simple S3 bucket, so you can see what it's like to deploy a stack for the first time. Afterwards, we will make changes to that bucket, so you see how CDK informs changes to an existing resource inside a stack.
Finally, we will add resources into the stack to explore this new CDK output.

There is a bonus step showing our strategy to replace the Jinja templates and how to clean up your environment at the end

Let's begin

## Step 1. Create an S3 bucket

After going through the step by step in the [README.md](/README.md) file, run `cdk synth`, which will synthesize the cloudformation template for the hello_cdk stack

The first part is what matters to us, which will define the CFN template to create the stack

```javascript
Resources:
  MyFirstBucketB8884501:
    Type: AWS::S3::Bucket
    Properties:
      VersioningConfiguration:
        Status: Enabled
    UpdateReplacePolicy: Retain
    DeletionPolicy: Retain
```
The rest are parameters and metadata added by CDK for analytics purposes, and do not interefere with your stack. Let's check differences to our current environment

`cdk diff`

```
(.venv) felipe@Felipes-MacBook-Pro rego_migration_demo % cdk diff
Stack HelloCdkStack
Parameters
[+] Parameter BootstrapVersion BootstrapVersion: {"Type":"AWS::SSM::Parameter::Value<String>","Default":"/cdk-bootstrap/hnb659fds/version","Description":"Version of the CDK Bootstrap resources in this environment, automatically retrieved from SSM Parameter Store. [cdk:skip]"}

Conditions
[+] Condition CDKMetadata/Condition CDKMetadataAvailable: {"Fn::Or":[{"Fn::Or":[{"Fn::Equals":[{"Ref":"AWS::Region"},"af-south-1"]},{"Fn::Equals":[{"Ref":"AWS::Region"},"ap-east-1"]},{"Fn::Equals":[{"Ref":"AWS::Region"},"ap-northeast-1"]},{"Fn::Equals":[{"Ref":"AWS::Region"},"ap-northeast-2"]},{"Fn::Equals":[{"Ref":"AWS::Region"},"ap-south-1"]},{"Fn::Equals":[{"Ref":"AWS::Region"},"ap-southeast-1"]},{"Fn::Equals":[{"Ref":"AWS::Region"},"ap-southeast-2"]},{"Fn::Equals":[{"Ref":"AWS::Region"},"ca-central-1"]},{"Fn::Equals":[{"Ref":"AWS::Region"},"cn-north-1"]},{"Fn::Equals":[{"Ref":"AWS::Region"},"cn-northwest-1"]}]},{"Fn::Or":[{"Fn::Equals":[{"Ref":"AWS::Region"},"eu-central-1"]},{"Fn::Equals":[{"Ref":"AWS::Region"},"eu-north-1"]},{"Fn::Equals":[{"Ref":"AWS::Region"},"eu-south-1"]},{"Fn::Equals":[{"Ref":"AWS::Region"},"eu-west-1"]},{"Fn::Equals":[{"Ref":"AWS::Region"},"eu-west-2"]},{"Fn::Equals":[{"Ref":"AWS::Region"},"eu-west-3"]},{"Fn::Equals":[{"Ref":"AWS::Region"},"me-south-1"]},{"Fn::Equals":[{"Ref":"AWS::Region"},"sa-east-1"]},{"Fn::Equals":[{"Ref":"AWS::Region"},"us-east-1"]},{"Fn::Equals":[{"Ref":"AWS::Region"},"us-east-2"]}]},{"Fn::Or":[{"Fn::Equals":[{"Ref":"AWS::Region"},"us-west-1"]},{"Fn::Equals":[{"Ref":"AWS::Region"},"us-west-2"]}]}]}

Resources
[+] AWS::S3::Bucket MyFirstBucket MyFirstBucketB8884501 

Other Changes
[+] Unknown Rules: {"CheckBootstrapVersion":{"Assertions":[{"Assert":{"Fn::Not":[{"Fn::Contains":[["1","2","3","4","5"],{"Ref":"BootstrapVersion"}]}]},"AssertDescription":"CDK bootstrap stack version 6 required. Please run 'cdk bootstrap' with a recent version of the CDK CLI."}]}}
```

As there is no existing stack called Hello CDK, CDK will then create a new one. It'll create an S3 Bucket resource called MyFirstBucketB8884501 (it adds randomness to resource IDs so there are no conflicts) and some more CDK related metadata. Let's deploy it

`cdk deploy`

Check the console or run `aws cloudformation describe-stacks --stack-name HelloCdkStack` to view your newly create stack. Now, if we run `cdk diff` again, it should tell us there are no differences to be deployed.

```
(.venv) felipe@Felipes-MacBook-Pro rego_migration_demo % cdk diff
Stack HelloCdkStack
There were no differences
```

## Step 2. Change some properties on existing resource

In the file hello_cdk_stack.py, uncomment lines 18 and 19, save and run `cdk diff` again.

```
(.venv) felipe@Felipes-MacBook-Pro rego_migration_demo % cdk diff
Stack HelloCdkStack
IAM Statement Changes
┌───┬────────────────┬────────┬────────────────┬────────────────┬───────────┐
│   │ Resource       │ Effect │ Action         │ Principal      │ Condition │
├───┼────────────────┼────────┼────────────────┼────────────────┼───────────┤
│ + │ ${Custom::S3Au │ Allow  │ sts:AssumeRole │ Service:lambda │           │
│   │ toDeleteObject │        │                │ .amazonaws.com │           │
│   │ sCustomResourc │        │                │                │           │
│   │ eProvider/Role │        │                │                │           │
│   │ .Arn}          │        │                │                │           │
├───┼────────────────┼────────┼────────────────┼────────────────┼───────────┤
│ + │ ${MyFirstBucke │ Allow  │ s3:DeleteObjec │ AWS:${Custom:: │           │
│   │ t.Arn}         │        │ t*             │ S3AutoDeleteOb │           │
│   │ ${MyFirstBucke │        │ s3:GetBucket*  │ jectsCustomRes │           │
│   │ t.Arn}/*       │        │ s3:List*       │ ourceProvider/ │           │
│   │                │        │                │ Role.Arn}      │           │
└───┴────────────────┴────────┴────────────────┴────────────────┴───────────┘
IAM Policy Changes
┌───┬───────────────────────────────────┬───────────────────────────────────┐
│   │ Resource                          │ Managed Policy ARN                │
├───┼───────────────────────────────────┼───────────────────────────────────┤
│ + │ ${Custom::S3AutoDeleteObjectsCust │ {"Fn::Sub":"arn:${AWS::Partition} │
│   │ omResourceProvider/Role}          │ :iam::aws:policy/service-role/AWS │
│   │                                   │ LambdaBasicExecutionRole"}        │
└───┴───────────────────────────────────┴───────────────────────────────────┘
(NOTE: There may be security-related changes not in this list. See https://github.com/aws/aws-cdk/issues/1299)

Resources
[+] AWS::S3::BucketPolicy MyFirstBucket/Policy MyFirstBucketPolicy3243DEFD 
[+] Custom::S3AutoDeleteObjects MyFirstBucket/AutoDeleteObjectsCustomResource MyFirstBucketAutoDeleteObjectsCustomResourceC52FCF6E 
[+] AWS::IAM::Role Custom::S3AutoDeleteObjectsCustomResourceProvider/Role CustomS3AutoDeleteObjectsCustomResourceProviderRole3B1BD092 
[+] AWS::Lambda::Function Custom::S3AutoDeleteObjectsCustomResourceProvider/Handler CustomS3AutoDeleteObjectsCustomResourceProviderHandler9D90184F 
[~] AWS::S3::Bucket MyFirstBucket MyFirstBucketB8884501 
 ├─ [+] Tags
 │   └─ [{"Key":"aws-cdk:auto-delete-objects","Value":"true"}]
 ├─ [~] DeletionPolicy
 │   ├─ [-] Retain
 │   └─ [+] Delete
 └─ [~] UpdateReplacePolicy
     ├─ [-] Retain
     └─ [+] Delete
```

You can check the differences in the Output above. Usually, IAM and Security Groups changes are shown separately for security reasons.
CDK will add some policies related to the functionality of the L2 Construct, but will not recreate the bucket, as this would be undesirable.

The tilda (~) represents changes to applied to an existing resource. In our case, one Tag will be added and two policies will be edited.

Let's deploy it. Run `cdk deploy` and check the changes in the console or CLI.

## Step 3. Add resources to an existing stack

In the file hello_cdk_stack.py, uncomment the rest of the HelloCdkStack class. Save the file and run `cdk diff` again.

```
(.venv) felipe@Felipes-MacBook-Pro rego_migration_demo % cdk diff
Stack HelloCdkStack
IAM Statement Changes
┌───┬─────────────────────────┬────────┬────────────────┬───────────────────────────────┬───────────┐
│   │ Resource                │ Effect │ Action         │ Principal                     │ Condition │
├───┼─────────────────────────┼────────┼────────────────┼───────────────────────────────┼───────────┤
│ + │ ${ASG/InstanceRole.Arn} │ Allow  │ sts:AssumeRole │ Service:ec2.${AWS::URLSuffix} │           │
└───┴─────────────────────────┴────────┴────────────────┴───────────────────────────────┴───────────┘
Security Group Changes
┌───┬──────────────────────────────────────┬─────┬────────────┬──────────────────────────────────────┐
│   │ Group                                │ Dir │ Protocol   │ Peer                                 │
├───┼──────────────────────────────────────┼─────┼────────────┼──────────────────────────────────────┤
│ + │ ${ASG/InstanceSecurityGroup.GroupId} │ In  │ TCP 80     │ ${LB/SecurityGroup.GroupId}          │
│ + │ ${ASG/InstanceSecurityGroup.GroupId} │ Out │ Everything │ Everyone (IPv4)                      │
├───┼──────────────────────────────────────┼─────┼────────────┼──────────────────────────────────────┤
│ + │ ${LB/SecurityGroup.GroupId}          │ In  │ TCP 80     │ Everyone (IPv4)                      │
│ + │ ${LB/SecurityGroup.GroupId}          │ Out │ TCP 80     │ ${ASG/InstanceSecurityGroup.GroupId} │
└───┴──────────────────────────────────────┴─────┴────────────┴──────────────────────────────────────┘
(NOTE: There may be security-related changes not in this list. See https://github.com/aws/aws-cdk/issues/1299)

Parameters
[+] Parameter SsmParameterValue:--aws--service--ami-amazon-linux-latest--amzn2-ami-hvm-x86_64-gp2:C96584B6-F00A-464E-AD19-53AFF4B05118.Parameter SsmParameterValueawsserviceamiamazonlinuxlatestamzn2amihvmx8664gp2C96584B6F00A464EAD1953AFF4B05118Parameter: {"Type":"AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>","Default":"/aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2"}

Resources
[+] AWS::EC2::VPC VPC VPCB9E5F0B4 
[+] AWS::EC2::Subnet VPC/PublicSubnet1/Subnet VPCPublicSubnet1SubnetB4246D30 
[+] AWS::EC2::RouteTable VPC/PublicSubnet1/RouteTable VPCPublicSubnet1RouteTableFEE4B781 
[+] AWS::EC2::SubnetRouteTableAssociation VPC/PublicSubnet1/RouteTableAssociation VPCPublicSubnet1RouteTableAssociation0B0896DC 
[+] AWS::EC2::Route VPC/PublicSubnet1/DefaultRoute VPCPublicSubnet1DefaultRoute91CEF279 
[+] AWS::EC2::EIP VPC/PublicSubnet1/EIP VPCPublicSubnet1EIP6AD938E8 
[+] AWS::EC2::NatGateway VPC/PublicSubnet1/NATGateway VPCPublicSubnet1NATGatewayE0556630 
[+] AWS::EC2::Subnet VPC/PublicSubnet2/Subnet VPCPublicSubnet2Subnet74179F39 
[+] AWS::EC2::RouteTable VPC/PublicSubnet2/RouteTable VPCPublicSubnet2RouteTable6F1A15F1 
[+] AWS::EC2::SubnetRouteTableAssociation VPC/PublicSubnet2/RouteTableAssociation VPCPublicSubnet2RouteTableAssociation5A808732 
[+] AWS::EC2::Route VPC/PublicSubnet2/DefaultRoute VPCPublicSubnet2DefaultRouteB7481BBA 
[+] AWS::EC2::EIP VPC/PublicSubnet2/EIP VPCPublicSubnet2EIP4947BC00 
[+] AWS::EC2::NatGateway VPC/PublicSubnet2/NATGateway VPCPublicSubnet2NATGateway3C070193 
[+] AWS::EC2::Subnet VPC/PrivateSubnet1/Subnet VPCPrivateSubnet1Subnet8BCA10E0 
[+] AWS::EC2::RouteTable VPC/PrivateSubnet1/RouteTable VPCPrivateSubnet1RouteTableBE8A6027 
[+] AWS::EC2::SubnetRouteTableAssociation VPC/PrivateSubnet1/RouteTableAssociation VPCPrivateSubnet1RouteTableAssociation347902D1 
[+] AWS::EC2::Route VPC/PrivateSubnet1/DefaultRoute VPCPrivateSubnet1DefaultRouteAE1D6490 
[+] AWS::EC2::Subnet VPC/PrivateSubnet2/Subnet VPCPrivateSubnet2SubnetCFCDAA7A 
[+] AWS::EC2::RouteTable VPC/PrivateSubnet2/RouteTable VPCPrivateSubnet2RouteTable0A19E10E 
[+] AWS::EC2::SubnetRouteTableAssociation VPC/PrivateSubnet2/RouteTableAssociation VPCPrivateSubnet2RouteTableAssociation0C73D413 
[+] AWS::EC2::Route VPC/PrivateSubnet2/DefaultRoute VPCPrivateSubnet2DefaultRouteF4F5CFD2 
[+] AWS::EC2::InternetGateway VPC/IGW VPCIGWB7E252D3 
[+] AWS::EC2::VPCGatewayAttachment VPC/VPCGW VPCVPCGW99B986DC 
[+] AWS::ElasticLoadBalancingV2::LoadBalancer LB LB8A12904C 
[+] AWS::EC2::SecurityGroup LB/SecurityGroup LBSecurityGroup8A41EA2B 
[+] AWS::EC2::SecurityGroupEgress LB/SecurityGroup/to HelloCdkStackASGInstanceSecurityGroupB8AFECB6:80 LBSecurityGrouptoHelloCdkStackASGInstanceSecurityGroupB8AFECB680937DEBD4 
[+] AWS::ElasticLoadBalancingV2::Listener LB/Listener LBListener49E825B4 
[+] AWS::ElasticLoadBalancingV2::TargetGroup LB/Listener/TargetGroup LBListenerTargetGroupF04FCF6D 
[+] AWS::EC2::SecurityGroup ASG/InstanceSecurityGroup ASGInstanceSecurityGroup0525485D 
[+] AWS::EC2::SecurityGroupIngress ASG/InstanceSecurityGroup/from HelloCdkStackLBSecurityGroupD21EA9DA:80 ASGInstanceSecurityGroupfromHelloCdkStackLBSecurityGroupD21EA9DA8092E1A5D3 
[+] AWS::IAM::Role ASG/InstanceRole ASGInstanceRoleE263A41B 
[+] AWS::IAM::InstanceProfile ASG/InstanceProfile ASGInstanceProfile0A2834D7 
[+] AWS::AutoScaling::LaunchConfiguration ASG/LaunchConfig ASGLaunchConfigC00AF12B 
[+] AWS::AutoScaling::AutoScalingGroup ASG/ASG ASG46ED3070 
[+] AWS::AutoScaling::ScalingPolicy ASG/ScalingPolicyAModestLoad ASGScalingPolicyAModestLoadC5714E5A 

Outputs
[+] Output LoadBalancer LoadBalancer: {"Value":{"Fn::GetAtt":["LB8A12904C","DNSName"]},"Export":{"Name":"LoadBalancer"}}


```
Also run `cdk synth` if you want to see the CFN template that will be applied to the stack.

As you might recall from previous conversations, L2 Constructs are create with several underlying assumptions. You can see this property for yourself in the output above. Even though we only asked for a VPC without any additional parameters, CDK also deploys several other resources it deems necessary for the correct functioning of your stack, such as Internet and NAT Gateways, Route Tables, rules and associations, etc.

You can override all of these if you want, but that's beyond our scope right now.

Deploy it.


## Bonus Step. Replacing Jinja templates

Another one of our goals is to remove Jinja templates from the codebase, and replace it with Python native syntax. I've added a simple feature flag which can remove or include part of the code to be synthesized by CDK.

During class instantiation, pass the `flag` variable either as `True` or `False` to change which resources will be created. In our case, toggling `flag` adds or removes the Load Balancer, Autoscaling Group and Output from our stack.

In step 3, as the flag was set to True, we created everything. Now, let's change the file app.py and set `flag` to `False`

#### **`app.py`**
```python
...
HelloCdkStack(app, "HelloCdkStack", flag=False)
...
```

Let's diff it

```
(.venv) felipe@Felipes-MacBook-Pro rego_migration_demo % cdk diff  
Stack HelloCdkStack
Security Group Changes
┌───┬─────────────────────────────────────────────┬─────┬──────────┬─────────────────────────────────────────────┐
│   │ Group                                       │ Dir │ Protocol │ Peer                                        │
├───┼─────────────────────────────────────────────┼─────┼──────────┼─────────────────────────────────────────────┤
│ - │ ${ASGInstanceSecurityGroup0525485D.GroupId} │ In  │ TCP 80   │ ${LBSecurityGroup8A41EA2B.GroupId}          │
├───┼─────────────────────────────────────────────┼─────┼──────────┼─────────────────────────────────────────────┤
│ - │ ${LBSecurityGroup8A41EA2B.GroupId}          │ Out │ TCP 80   │ ${ASGInstanceSecurityGroup0525485D.GroupId} │
└───┴─────────────────────────────────────────────┴─────┴──────────┴─────────────────────────────────────────────┘
(NOTE: There may be security-related changes not in this list. See https://github.com/aws/aws-cdk/issues/1299)

Parameters
[-] Parameter SsmParameterValueawsserviceamiamazonlinuxlatestamzn2amihvmx8664gp2C96584B6F00A464EAD1953AFF4B05118Parameter: {"Type":"AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>","Default":"/aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2"}

Resources
[-] AWS::ElasticLoadBalancingV2::LoadBalancer LB8A12904C destroy
[-] AWS::EC2::SecurityGroup LBSecurityGroup8A41EA2B destroy
[-] AWS::EC2::SecurityGroupEgress LBSecurityGrouptoHelloCdkStackASGInstanceSecurityGroupB8AFECB680937DEBD4 destroy
[-] AWS::ElasticLoadBalancingV2::Listener LBListener49E825B4 destroy
[-] AWS::ElasticLoadBalancingV2::TargetGroup LBListenerTargetGroupF04FCF6D destroy
[-] AWS::EC2::SecurityGroup ASGInstanceSecurityGroup0525485D destroy
[-] AWS::EC2::SecurityGroupIngress ASGInstanceSecurityGroupfromHelloCdkStackLBSecurityGroupD21EA9DA8092E1A5D3 destroy
[-] AWS::IAM::Role ASGInstanceRoleE263A41B destroy
[-] AWS::IAM::InstanceProfile ASGInstanceProfile0A2834D7 destroy
[-] AWS::AutoScaling::LaunchConfiguration ASGLaunchConfigC00AF12B destroy
[-] AWS::AutoScaling::AutoScalingGroup ASG46ED3070 destroy
[-] AWS::AutoScaling::ScalingPolicy ASGScalingPolicyAModestLoadC5714E5A destroy

Outputs
[-] Output LoadBalancer: {"Value":{"Fn::GetAtt":["LB8A12904C","DNSName"]},"Export":{"Name":"LoadBalancer"}}
```

Now, since LB, ASG and Output creation conditions were not met, they are not part of the stack anymore. CDK detects this difference and will delete those resources if we deploy.

## Clean-up

Run `cdk destroy` to delete the stack and all resources associated with it.


