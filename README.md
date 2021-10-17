# Simplifying service discovery for multi-account architecture using App Mesh
## License Type: MIT-0
## Pre-requisites for running this demo:
1.	Two AWS Account which are part of same AWS Organization

If you want to modify the code you will need to:
•	create a Cloud9 Environment and push it to your image repository (Amazon ECR Private or Public or any other repo)

## Code for the demo:
•	Source code for the sample flask code used in this example is at – git clone https://github.com/aws-samples/aws-app-mesh-multi-cell-multi-account/application-code. If you want to modify the code you do the same using AWS Cloud 9
•	IaC code for deployment steps are depicted at - https://github.com/aws-samples/aws-app-mesh-multi-cell-multi-account/cloudformation-templates


## Deployment Steps:

Account and IAM user creation:
•	In both the AWS Accounts i.e. account 1 and account 2, create one IAM user each and get the Access key and Secret Key (here i have assumed administrator access, but you can grant least privilege CLI access for AppMesh, ECS, CloudMap, Route53 etc)

Cloud9 setup and AWS Profile configuration:
•	In account1, create and  Cloud9 environment (don’t assign any IAM role to this cloud9 and turn off AWS managed temporary credentials). Open a new terminal in Cloud9 and run below commands two create AWS profiles: 
a.	aws configure --profile acct1-domain1 (pass the access key and secret key created in step 1, region as us-east-1)
b.	aws configure --profile acct2-domain2 (pass the access key and secret key created in step 1, region as us-east-1)
Here we will use us-east-1 but you can use region of your choice. (Please note AppMesh is a regional construct and cannot span regions)
•	Optional Step - If you want to refer the source code of the docker images that we will use for this demo, you can refer  Github link - <<github link for sourcecode>>
•	We will clone the Infrastructure as a Code (IaC) for deployment of AWS resources via the command “git clone <<githublink>>
Cd <<folderpath>>

Setup infra – VPC, Subnets, App Mesh resources required for the demo in AWS Account 1
•	export Account1AccountId=XXXXXXXXXXXX (your 12 digit AWS Account number). Post setting check echo $Account1AccountId
•	export Account2AccountId=XXXXXXXXXXXX (your 12 digit AWS Account number). Post setting check echo $Account2AccountId
•	aws --profile acct1-domain1 cloudformation deploy --no-fail-on-empty-changeset --stack-name appmesh-vpc-subnet-infra --template-file "1_infra_account_1.yaml" --capabilities CAPABILITY_IAM
This will create VPC, two public  subnets (with IGW) and two private subnets (with NAT Gateway). Please update the CIDR as per your networking requirements
•	aws --profile acct1-domain1 cloudformation deploy --no-fail-on-empty-changeset --stack-name appmesh-resources-account-1 --template-file "2_appmesh_resources.yaml" --parameter-overrides MeshOwner=$Account1AccountId --capabilities CAPABILITY_IAM
This will create App Mesh resources like Virtual Nodes, Virtual Service for Service A and B Cell1 and Cell2 and Virtual Router for Service B

Share the VPC and Mesh created in Account1 with Account2 using Resource Access Manager:
•	aws --profile acct1-domain1 cloudformation deploy --no-fail-on-empty-changeset --stack-name mesh-and-vpc-share --template-file "3_mesh_and_vpc_share.yaml" --parameter-overrides Account2AccountId=$Account2AccountId --capabilities CAPABILITY_IAM

Create common infra components in AWS Account 1: 
•	aws --profile acct1-domain1 cloudformation deploy --no-fail-on-empty-changeset --stack-name common-infra-account-1 --template-file "4_common_infra_account_1.yaml" --capabilities CAPABILITY_NAMED_IAM
This will create ECS Cluster, Cloud Map Namespace (internal-Domain1.com), CloudWatch log group, IAM Roles and Security Group
•	aws --profile acct1-domain1 cloudformation deploy --no-fail-on-empty-changeset --stack-name ALB-for-Service-A --template-file "5_ALB-for-Service-A.yaml" --capabilities CAPABILITY_IAM
This stack creates Application Load Balancer, Target Group, Listener and Rules. ALB is for Service A, Cell 1 and Cell 2 having two different Target Groups. Later in this demo we can point ALB to a Front end service using App Mesh Virtual Gateway

Create Service A and B, Cell1 and Cell2 ECS Tasks and Definitions in Account 1:  		
Each ECS Task definition has 3 container definitions – Application container, Envoy sidecar and Xray daemon. For now we have configured application container from dockerhub, but you can provide your own application image from Amazon ECR or any other private repository
•	aws --profile acct1-domain1 cloudformation deploy --no-fail-on-empty-changeset --stack-name Domain-1-Service-B-Cell-1 --template-file "7a_Domain-1-Service-B-Cell-1.yaml" --parameter-overrides MeshOwner=$Account1AccountId --capabilities CAPABILITY_IAM
This creates ECS Task and Service for Service-B-Cell-1 in AWS Account 1
•	aws --profile acct1-domain1 cloudformation deploy --no-fail-on-empty-changeset --stack-name Domain-1-Service-B-Cell-2 --template-file "7b_Domain-1-Service-B-Cell-2.yaml" --parameter-overrides MeshOwner=$Account1AccountId --capabilities CAPABILITY_IAM
This creates ECS Task and Service for Service-B-Cell-2 in AWS Account 1
•	aws --profile acct1-domain1 cloudformation deploy --no-fail-on-empty-changeset --stack-name Domain-1-Service-A-Cell-1 --template-file "6a_Domain-1-Service-A-Cell-1.yaml" --parameter-overrides MeshOwner=$Account1AccountId --capabilities CAPABILITY_IAM
This creates ECS Task and Service for Service-A-Cell-1 in AWS Account 1
•	aws --profile acct1-domain1 cloudformation deploy --no-fail-on-empty-changeset --stack-name Domain-1-Service-A-Cell-2 --template-file "6b_Domain-1-Service-A-Cell-2.yaml" --parameter-overrides MeshOwner=$Account1AccountId --capabilities CAPABILITY_IAM
This creates ECS Task and Service for Service-A-Cell-2 in AWS account 1

Create common Infra components in AWS Account 2:
•	aws --profile acct2-domain2 cloudformation deploy --no-fail-on-empty-changeset --stack-name common-infra-account-2 --template-file "8_common_infra_account_2.yaml" --parameter-overrides MeshOwner=$Account1AccountId "VPC=$(aws --profile acct2-domain2 ec2 describe-vpcs --filters Name=owner-id,Values=$Account1AccountId --query 'Vpcs[*].VpcId' --output text)" --capabilities CAPABILITY_NAMED_IAM
This will create ECS Cluster, CloudWatch log group, IAM Roles and Security Group

Create App Mesh resources in AWS Account 2:
•	aws --profile acct2-domain2 cloudformation deploy --no-fail-on-empty-changeset --stack-name appmesh-resources-account-2 --template-file "9_appmesh_resources_account_2.yaml" --parameter-overrides MeshOwner=$Account1AccountId --capabilities CAPABILITY_IAM
•	This stack creates Virtual Service, Virtual Node and Virtual Router for Service-X Cell1 and Cell2

Detailed steps to create Cloud Map Namespace (internal-Domain2.com) in AWS Account 2 and associating with Shared VPC:
a.	aws --profile acct2-domain2 ec2 describe-vpcs --filters Name=owner-id,Values=$Account2AccountId --query 'Vpcs[*].VpcId' --output text
Basically, this checks for any existing VPC in AWS Account2 (not the shared VPC). Refer this documentation which states “When you create a private hosted zone, you must associate a VPC with the hosted zone, and the VPC that you specify must have been created by using the same account that you're using to create the hosted zone.”
If you don’t have any VPC created in your Account2, please create one temporarily for this step using command aws --profile acct2-domain2 ec2 create-vpc --cidr-block 192.168.0.0/28 (We can remove this VPC and association later)
b.	aws --profile acct2-domain2 servicediscovery create-private-dns-namespace --name internal-Domain2.com --vpc <<vpc-id-from-step-a>>
To track the creation of private DNS namespace please use the command:
aws --profile acct2-domain2 servicediscovery get-operation --operation-id <<operationid-received-in-above-step>> (here the status should to SUCCESS)
This will create the private-dns-namespace in CloudMap+Route53, but we have not yet associated this private DNS with Shared VPC id. We will perform below steps to associate this DNS with shared VPC
c.	aws --profile acct2-domain2 servicediscovery list-namespaces --query "Namespaces[?Name == 'internal-Domain2.com'].Properties.DnsProperties.HostedZoneId" --output text
This step gives us the Route53 Hosted Zone Id
d.	aws --profile acct2-domain2 ec2 describe-vpcs --filters Name=owner-id,Values=$Account1AccountId --query 'Vpcs[*].VpcId' --output text
This step gives us the VPC Id of the Shared VPC (we are checking where owner is account 1)
e.	aws route53 create-vpc-association-authorization --hosted-zone-id <<as-per-step-c>> --vpc VPCRegion=<<your-AWS-region>>,VPCId=<<as-per-step-d>> --region <<your-AWS-region>> --profile acct2-domain2
Here please replace the AWS region you are working in. This step i.e. “create-vpc-association-authorization” creates request to associate the hosted zone created for namespace “internal-Domain2.com” in AWS Account 2 with Shared VPC created in AWS Account 1 (if you see we are using profile as account2).
f.	aws route53 associate-vpc-with-hosted-zone --hosted-zone-id <<as-per-step-c>> --vpc VPCRegion=<<your-AWS-region>>,VPCId=<<as-per-step-d>> --region <<your-AWS-region>> --profile acct1-domain1
This is approval from user in account1 to approve the association. Here again, please replace the AWS region you are working in. This step i.e. “associate-vpc-with-hosted-zone” uses profile as account 1 which means we are approving the authorization created in above step i.e. authorizing the hosted zone/namespace created in account 2 to be associated with VPC in account 1. 
Above command returns Change Id and the initial status is “Pending”. 
g.	aws --profile acct2-domain2 route53 get-change --id "/change/CXXXXXXXXXX" --region <<your-AWS-region>>
Provide the change id received in step f. To confirm if the status has changed to desired state i.e. “INSYNC” (profile should be account 2) 


PS: If you have multiple AWS accounts(Hub-and-Spoke), you might want to create automation of these CLI commands using --filters and --query options

Create Service X Cell1 and Cell2 ECS Tasks and Definitions in Account 2:
•	aws --profile acct2-domain2 cloudformation deploy --no-fail-on-empty-changeset --stack-name Domain-2-Service-X-Cell-1 --template-file "10a_Domain-2-Service-X-Cell-1.yaml" --parameter-overrides MeshOwner=$Account1AccountId "VPC=$(aws --profile acct1-domain1 cloudformation describe-stacks --stack-name=appmesh-vpc-subnet-infra --query="Stacks[0].Outputs[?OutputKey=='VPC'].OutputValue" --output=text)" "PrivateSubnet1=$(aws --profile acct1-domain1 cloudformation describe-stacks --stack-name=appmesh-vpc-subnet-infra --query="Stacks[0].Outputs[?OutputKey=='PrivateSubnet1'].OutputValue" --output=text)" "PrivateSubnet2=$(aws --profile acct1-domain1 cloudformation describe-stacks --stack-name=appmesh-vpc-subnet-infra --query="Stacks[0].Outputs[?OutputKey=='PrivateSubnet2'].OutputValue" --output=text)" "NameSpaceId2=$(aws --profile acct2-domain2 servicediscovery list-namespaces --query "Namespaces[?Name == 'internal-Domain2.com'].Id" --output text)" --capabilities CAPABILITY_IAM
•	aws --profile acct2-domain2 cloudformation deploy --no-fail-on-empty-changeset --stack-name Domain-2-Service-X-Cell-2 --template-file "10b_Domain-2-Service-X-Cell-2.yaml" --parameter-overrides MeshOwner=$Account1AccountId "VPC=$(aws --profile acct1-domain1 cloudformation describe-stacks --stack-name=appmesh-vpc-subnet-infra --query="Stacks[0].Outputs[?OutputKey=='VPC'].OutputValue" --output=text)" "PrivateSubnet1=$(aws --profile acct1-domain1 cloudformation describe-stacks --stack-name=appmesh-vpc-subnet-infra --query="Stacks[0].Outputs[?OutputKey=='PrivateSubnet1'].OutputValue" --output=text)" "PrivateSubnet2=$(aws --profile acct1-domain1 cloudformation describe-stacks --stack-name=appmesh-vpc-subnet-infra --query="Stacks[0].Outputs[?OutputKey=='PrivateSubnet2'].OutputValue" --output=text)" "NameSpaceId2=$(aws --profile acct2-domain2 servicediscovery list-namespaces --query "Namespaces[?Name == 'internal-Domain2.com'].Id" --output text)" --capabilities CAPABILITY_IAM

This completes the demo setup, now you can grab and ALB DNS from output of CloudFormation stack “ALB-for-Service-A” and test your functionality. Also check the AWS X-Ray Service Map by going to X-Ray in your AWS console. You can change the weights of RouterB and RouterX in App Mesh
•	aws --profile acct1-domain1 appmesh update-route --cli-input-json file://AppMesh-Router-B-config-change.json
Before running above aommand, update the meshOwner as 12-digit AWS account number of AWS Account 1
•	aws --profile acct2-domain2 appmesh update-route --cli-input-json file://AppMesh-Router-X-config-change.json
Before running above command, update the meshOwner as 12-digit AWS account number of AWS Account 1

Last optional step:
For Service A, if you want to use App Mesh Virtual Gateway instead of Application Load Balancer, we need to create a Virtual Gateway in App Mesh, then create Frond-End ECS Task (which will have only one container that is Envoy) and ECS Service which will tie to new Front-End Application Load Balancer. Then create Gateway Routes to point the external traffic as ALB to Virtual Gateway to Virtual Service to Virtual Router and finally to Virtual Node 

•	aws --profile acct1-domain1 cloudformation deploy --no-fail-on-empty-changeset --stack-name AppMesh-Virtual-Gateway-resources --template-file "11_Virtual-Gateway-AppMesh-resources.yaml" --parameter-overrides MeshOwner=$Account1AccountId --capabilities CAPABILITY_IAM
The above step will create App Mesh Virtual Gateway, Router for Service A (as earlier Service A had Application Load Balancer Target Group), Virtual Gateway Routes for Service A, B and C pointing to respective services, which in turn point to respective routers
•	aws --profile acct1-domain1 cloudformation deploy --no-fail-on-empty-changeset --stack-name Virtual-Gateway-Load-Balancer --template-file "12_FrontEnd-ECS-Task-and-Service-for-Virtual-Gateway.yaml" --capabilities CAPABILITY_IAM
The above stack will create ECS Task with only Envoy container for Virtual Gateway, will create ECS Service for the task and register with a new FrontEnd Load Balancer
Post the above step is created, grab the output of the stack “Virtual-Gateway-Load-Balancer” and hit the load balancer endpoint with suffix as /servicea, /serviceb and /servicex to see that Front End Load Balancer to Virtual Gateway to Gateway routers pointing to Virtual Services.

## License
This sample is licensed under the MIT-0 License. See the LICENSE file.
