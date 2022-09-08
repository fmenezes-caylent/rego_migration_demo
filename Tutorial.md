# Checking out CDK's logging using `cdk synth` and `cdk diff`

Before using this tutorial, follow the instructions on [README.md](/README.md) file to setup your environment.

Our goal is to be able to see changes in stacks prior to deployiment. To accomplish that, we will create two stacks so we get acquainted to CDK inner workings.

Compute stack is comprised of a VPC, an Autoscaling group, a Load Balancer, and a CFN Output with the LB's DNS address.
Storage stack is an S3 bucket with a policy flag.

This guide is divided into 3 steps. First, we will deploy Storage Stack, so you can see what it's like to deploy a stack for the first time. Afterwards, we will make changes to resource properties, so you see how CDK informs changes to an existing resource inside a stack. This step will also show our strategy to replacing Jinja templates.
Finally, we will deploy Compute Stack in the same CDK app, to test CDK's hability to update only the stack with changes.

Let's begin

## Step 1. Create an S3 bucket

After going through the step by step in the [README.md](/README.md) file, run `cdk ls`, which will list the stacks in our app

```
(.venv) felipe@Felipes-MacBook-Pro rego_migration_demo % cdk ls
storage-stack
```

Now, run `cdk synth`, which will synthesize the cloudformation template.

The first part is what matters to us, which will define the CFN template to create the stack.

```yaml
Resources:
  S3Bucket07682993:
    Type: AWS::S3::Bucket
    UpdateReplacePolicy: Retain
    DeletionPolicy: Retain
    Metadata:
```
Note: Even though we are synthesizing Cloudformation templates, it's important to have in mind that the stack management will be done by CDK. CDK acts like a wrapper for Cloudformation. CDK Synthesize is only used for verification. All deployments are supposed to be done through `cdk deploy`

The rest of the template is comprised of parameters and metadata added by CDK for analytics purposes, and do not interefere with your stack. Let's check differences to our current environment.

`cdk diff`

```
(.venv) felipe@Felipes-MacBook-Pro rego_migration_demo % cdk diff
Stack storage-stack
Parameters
[+] Parameter BootstrapVersion BootstrapVersion: {"Type":"AWS::SSM::Parameter::Value<String>","Default":"/cdk-bootstrap/hnb659fds/version","Description":"Version of the CDK Bootstrap resources in this environment, automatically retrieved from SSM Parameter Store. [cdk:skip]"}

Conditions
[+] Condition CDKMetadata/Condition CDKMetadataAvailable: {"Fn::Or":[{"Fn::Or":[{"Fn::Equals":[{"Ref":"AWS::Region"},"af-south-1"]},{"Fn::Equals":[{"Ref":"AWS::Region"},"ap-east-1"]},{"Fn::Equals":[{"Ref":"AWS::Region"},"ap-northeast-1"]},{"Fn::Equals":[{"Ref":"AWS::Region"},"ap-northeast-2"]},{"Fn::Equals":[{"Ref":"AWS::Region"},"ap-south-1"]},{"Fn::Equals":[{"Ref":"AWS::Region"},"ap-southeast-1"]},{"Fn::Equals":[{"Ref":"AWS::Region"},"ap-southeast-2"]},{"Fn::Equals":[{"Ref":"AWS::Region"},"ca-central-1"]},{"Fn::Equals":[{"Ref":"AWS::Region"},"cn-north-1"]},{"Fn::Equals":[{"Ref":"AWS::Region"},"cn-northwest-1"]}]},{"Fn::Or":[{"Fn::Equals":[{"Ref":"AWS::Region"},"eu-central-1"]},{"Fn::Equals":[{"Ref":"AWS::Region"},"eu-north-1"]},{"Fn::Equals":[{"Ref":"AWS::Region"},"eu-south-1"]},{"Fn::Equals":[{"Ref":"AWS::Region"},"eu-west-1"]},{"Fn::Equals":[{"Ref":"AWS::Region"},"eu-west-2"]},{"Fn::Equals":[{"Ref":"AWS::Region"},"eu-west-3"]},{"Fn::Equals":[{"Ref":"AWS::Region"},"me-south-1"]},{"Fn::Equals":[{"Ref":"AWS::Region"},"sa-east-1"]},{"Fn::Equals":[{"Ref":"AWS::Region"},"us-east-1"]},{"Fn::Equals":[{"Ref":"AWS::Region"},"us-east-2"]}]},{"Fn::Or":[{"Fn::Equals":[{"Ref":"AWS::Region"},"us-west-1"]},{"Fn::Equals":[{"Ref":"AWS::Region"},"us-west-2"]}]}]}

Resources
[+] AWS::S3::Bucket S3Bucket S3Bucket07682993 

Other Changes
[+] Unknown Rules: {"CheckBootstrapVersion":{"Assertions":[{"Assert":{"Fn::Not":[{"Fn::Contains":[["1","2","3","4","5"],{"Ref":"BootstrapVersion"}]}]},"AssertDescription":"CDK bootstrap stack version 6 required. Please run 'cdk bootstrap' with a recent version of the CDK CLI."}]}}
```

As there is no existing stack called "storage-stack", CDK will then create a new one. It'll create an S3 Bucket resource called S3Bucket07682993 (it adds some randomness to resource IDs so there are no conflicts) and some more CDK related metadata. Let's deploy it

`cdk deploy`

Check the console or run `aws cloudformation describe-stacks --stack-name storage-stack` to view your newly create stack. Now, if we run `cdk diff` again, it should tell us there are no differences to be deployed.

```
(.venv) felipe@Felipes-MacBook-Pro rego_migration_demo % cdk diff
Stack storage-stack
There were no differences
```

## Step 2. Change some properties on existing resource

In the file app.py, change the policy flag to `True` and save the file

**app.py**
```python
StorageStack(app, "storage-stack", policy_flag=True)
```
Then, run `cdk diff` again

```
(.venv) felipe@Felipes-MacBook-Pro rego_migration_demo % cdk diff
Stack storage-stack
IAM Statement Changes
┌───┬──────────────────────────────────────────────────────┬────────┬──────────────────────────────────────────────────────┬───────────────────────────────────────────────────────┬───────────┐
│   │ Resource                                             │ Effect │ Action                                               │ Principal                                             │ Condition │
├───┼──────────────────────────────────────────────────────┼────────┼──────────────────────────────────────────────────────┼───────────────────────────────────────────────────────┼───────────┤
│ + │ ${Custom::S3AutoDeleteObjectsCustomResourceProvider/ │ Allow  │ sts:AssumeRole                                       │ Service:lambda.amazonaws.com                          │           │
│   │ Role.Arn}                                            │        │                                                      │                                                       │           │
├───┼──────────────────────────────────────────────────────┼────────┼──────────────────────────────────────────────────────┼───────────────────────────────────────────────────────┼───────────┤
│ + │ ${S3Bucket.Arn}                                      │ Allow  │ s3:DeleteObject*                                     │ AWS:${Custom::S3AutoDeleteObjectsCustomResourceProvid │           │
│   │ ${S3Bucket.Arn}/*                                    │        │ s3:GetBucket*                                        │ er/Role.Arn}                                          │           │
│   │                                                      │        │ s3:List*                                             │                                                       │           │
└───┴──────────────────────────────────────────────────────┴────────┴──────────────────────────────────────────────────────┴───────────────────────────────────────────────────────┴───────────┘
IAM Policy Changes
┌───┬───────────────────────────────────────────────────────────┬──────────────────────────────────────────────────────────────────────────────────────────────┐
│   │ Resource                                                  │ Managed Policy ARN                                                                           │
├───┼───────────────────────────────────────────────────────────┼──────────────────────────────────────────────────────────────────────────────────────────────┤
│ + │ ${Custom::S3AutoDeleteObjectsCustomResourceProvider/Role} │ {"Fn::Sub":"arn:${AWS::Partition}:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"} │
└───┴───────────────────────────────────────────────────────────┴──────────────────────────────────────────────────────────────────────────────────────────────┘
(NOTE: There may be security-related changes not in this list. See https://github.com/aws/aws-cdk/issues/1299)

Resources
[+] AWS::S3::BucketPolicy S3Bucket/Policy S3BucketPolicyF560589A 
[+] Custom::S3AutoDeleteObjects S3Bucket/AutoDeleteObjectsCustomResource S3BucketAutoDeleteObjectsCustomResource7735AB63 
[+] AWS::IAM::Role Custom::S3AutoDeleteObjectsCustomResourceProvider/Role CustomS3AutoDeleteObjectsCustomResourceProviderRole3B1BD092 
[+] AWS::Lambda::Function Custom::S3AutoDeleteObjectsCustomResourceProvider/Handler CustomS3AutoDeleteObjectsCustomResourceProviderHandler9D90184F 
[~] AWS::S3::Bucket S3Bucket S3Bucket07682993 
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

Note: With this syntax, we can remove the Jinja functionality and replace it with Python native code.

Let's deploy it. Run `cdk deploy` and check the changes in the console or CLI.

## Step 3. Add a new stack to the app

In the file app.py, uncomment line 12. If you run `cdk ls` again, you'll see our app has now an additional stack.

Save the file and run `cdk diff` again. I'll remove CDK parameters and metadata for clarity.

```
(.venv) felipe@Felipes-MacBook-Pro rego_migration_demo % cdk diff
Stack compute-stack
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

---
*** CDK specific params and metadata removed for clarity***
---

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
[+] AWS::EC2::SecurityGroupEgress LB/SecurityGroup/to computestackASGInstanceSecurityGroup45242DB9:80 LBSecurityGrouptocomputestackASGInstanceSecurityGroup45242DB9808EAB03BB 
[+] AWS::ElasticLoadBalancingV2::Listener LB/Listener LBListener49E825B4 
[+] AWS::ElasticLoadBalancingV2::TargetGroup LB/Listener/TargetGroup LBListenerTargetGroupF04FCF6D 
[+] AWS::EC2::SecurityGroup ASG/InstanceSecurityGroup ASGInstanceSecurityGroup0525485D 
[+] AWS::EC2::SecurityGroupIngress ASG/InstanceSecurityGroup/from computestackLBSecurityGroup00BDBE52:80 ASGInstanceSecurityGroupfromcomputestackLBSecurityGroup00BDBE5280070DCF0D 
[+] AWS::IAM::Role ASG/InstanceRole ASGInstanceRoleE263A41B 
[+] AWS::IAM::InstanceProfile ASG/InstanceProfile ASGInstanceProfile0A2834D7 
[+] AWS::AutoScaling::LaunchConfiguration ASG/LaunchConfig ASGLaunchConfigC00AF12B 
[+] AWS::AutoScaling::AutoScalingGroup ASG/ASG ASG46ED3070 
[+] AWS::AutoScaling::ScalingPolicy ASG/ScalingPolicyAModestLoad ASGScalingPolicyAModestLoadC5714E5A 

Outputs
[+] Output LoadBalancer LoadBalancer: {"Value":{"Fn::GetAtt":["LB8A12904C","DNSName"]},"Export":{"Name":"LoadBalancer"}}

Other Changes
[+] Unknown Rules: {"CheckBootstrapVersion":{"Assertions":[{"Assert":{"Fn::Not":[{"Fn::Contains":[["1","2","3","4","5"],{"Ref":"BootstrapVersion"}]}]},"AssertDescription":"CDK bootstrap stack version 6 required. Please run 'cdk bootstrap' with a recent version of the CDK CLI."}]}}

Stack storage-stack
There were no differences
```
From the output, we can see that, for compute-stack, several resources will be added, while CDK acknowledges no changes exist for storage-stack.

Also run `cdk synth` if you want to see the CFN template that will be applied to the stack.

As you might recall from previous conversations, L2 Constructs are create with several underlying assumptions. You can see this property for yourself in the output above. For instance, in the VPC case, even though we only asked for a VPC without any additional parameters, CDK also deploys several other resources it deems necessary for the correct functioning of your stack, such as Internet and NAT Gateways, Route Tables, rules and associations, among others.

You can override all of these if you want, but that's beyond our scope right now.

Deploy it.

```
(.venv) felipe@Felipes-MacBook-Pro rego_migration_demo % cdk deploy

Since this app includes more than a single stack, specify which stacks to use (wildcards are supported) or specify `--all`
Stacks: compute-stack · storage-stack
(.venv) felipe@Felipes-MacBook-Pro rego_migration_demo % 
```
Oops. Since we have more than one stack in our app, CDK asks us to chose which one we would like to deploy. Let's add the `--all` flag.

`cdk deploy --all`

Wait for a few minutes while CDK is creating the stack and check the console for the new stack.

```
(.venv) felipe@Felipes-MacBook-Pro rego_migration_demo % cdk deploy --all

✨  Synthesis time: 4.18s

compute-stack: building assets...

[0%] start: Building 35a5dc91a9236b732409b97e5c31bf8efc0cc425a2daec6f4ac8b34aea70799a:current_account-current_region
[100%] success: Built 35a5dc91a9236b732409b97e5c31bf8efc0cc425a2daec6f4ac8b34aea70799a:current_account-current_region

compute-stack: assets built

storage-stack: building assets...

[0%] start: Building e57c1acaa363d7d2b81736776007a7091bc73dff4aeb8135627c4511a51e7dca:current_account-current_region
[0%] start: Building e7cf96f82293a8d9d45cf5d4ebb11ff30001947aeb0c88fc14fe1712d98fbd99:current_account-current_region
[50%] success: Built e57c1acaa363d7d2b81736776007a7091bc73dff4aeb8135627c4511a51e7dca:current_account-current_region
[100%] success: Built e7cf96f82293a8d9d45cf5d4ebb11ff30001947aeb0c88fc14fe1712d98fbd99:current_account-current_region

storage-stack: assets built

compute-stack
This deployment will make potentially sensitive changes according to your current security approval level (--require-approval broadening).
Please confirm you intend to make the following modifications:

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

Do you wish to deploy these changes (y/n)? y
compute-stack: deploying...
[0%] start: Publishing 35a5dc91a9236b732409b97e5c31bf8efc0cc425a2daec6f4ac8b34aea70799a:current_account-current_region
[100%] success: Published 35a5dc91a9236b732409b97e5c31bf8efc0cc425a2daec6f4ac8b34aea70799a:current_account-current_region
compute-stack: creating CloudFormation changeset...

 ✅  compute-stack

✨  Deployment time: 262.99s

Outputs:
compute-stack.LoadBalancer = compu-LB8A1-11PIR01PH1JJ4-1960672414.eu-central-1.elb.amazonaws.com
Stack ARN:
arn:aws:cloudformation:eu-central-1:360586975922:stack/compute-stack/5868a800-2fa0-11ed-aa6a-02ad05695340

✨  Total time: 267.17s

storage-stack
storage-stack: deploying...
[0%] start: Publishing e57c1acaa363d7d2b81736776007a7091bc73dff4aeb8135627c4511a51e7dca:current_account-current_region
[0%] start: Publishing e7cf96f82293a8d9d45cf5d4ebb11ff30001947aeb0c88fc14fe1712d98fbd99:current_account-current_region
[50%] success: Published e57c1acaa363d7d2b81736776007a7091bc73dff4aeb8135627c4511a51e7dca:current_account-current_region
[100%] success: Published e7cf96f82293a8d9d45cf5d4ebb11ff30001947aeb0c88fc14fe1712d98fbd99:current_account-current_region

 ✅  storage-stack (no changes)

✨  Deployment time: 7.84s

Stack ARN:
arn:aws:cloudformation:eu-central-1:360586975922:stack/storage-stack/59405540-2f9e-11ed-93ce-021585fe04e8

✨  Total time: 12.02s
```
## Bonus step: Add resources to existing stack

Let's add a second S3 Bucket to the storage-stack. Uncomment line 20 from `storage-stack.py` and save the file. Let's check again outputs for cdk diff.

```
(.venv) felipe@Felipes-MacBook-Pro rego_migration_demo % cdk diff
Stack compute-stack
There were no differences
Stack storage-stack
Resources
[+] AWS::S3::Bucket S3Bucket-2 S3Bucket220DBF58B 
```

Again, it recognizes there are no differences for the unchanged stack, and lists the new resource to be added to storage-stack (our new S3 bucket).


Deploy it:

`cdk deploy storage-stack`


## Clean-up

Run `cdk destroy` to delete the stack and all resources associated with it.


