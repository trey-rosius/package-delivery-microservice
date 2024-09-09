import * as cdk from "aws-cdk-lib";
import { Construct } from "constructs";
import * as ec2 from "aws-cdk-lib/aws-ec2";
import * as ecs from "aws-cdk-lib/aws-ecs";
import * as ecs_patterns from "aws-cdk-lib/aws-ecs-patterns";
import * as apigw2 from "aws-cdk-lib/aws-apigatewayv2";
import * as ecr from "aws-cdk-lib/aws-ecr";
import * as logs from "aws-cdk-lib/aws-logs";
import * as iam from "aws-cdk-lib/aws-iam";
import { HttpAlbIntegration } from "aws-cdk-lib/aws-apigatewayv2-integrations";

import { ServicePort } from "./service-port";

export class PackageDeliveryMicroserviceStack extends cdk.Stack {
  PREFIX = "PACKAGE-DELIVERY-MICROSERVICE";
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const servicesPorts: ServicePort[] = [
      new ServicePort("user-service", 5001),
      new ServicePort("package-service", 5002),
      new ServicePort("pickup-service", 5003),
      new ServicePort("notification-service", 5004),
      new ServicePort("delivery-service", 5005),
      new ServicePort("payment-service", 5006),
    ];

    const vpc = new ec2.Vpc(this, "EdaVpc", {
      ipAddresses: ec2.IpAddresses.cidr("10.0.0.0/16"),
      maxAzs: 2, // Default is all AZs in region
      vpcName: `${this.PREFIX}-mvpc`,

      restrictDefaultSecurityGroup: false,
    });
    // Create Log Group
    const vpcLogGroup = new logs.LogGroup(this, "VPCLogGroup", {
      logGroupName: "ecs-cdk-vpc-flow",
      retention: logs.RetentionDays.ONE_DAY,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    // Create IAM Role
    const vpcFlowRole = new iam.Role(this, "FlowLog", {
      assumedBy: new iam.ServicePrincipal("vpc-flow-logs.amazonaws.com"),
      inlinePolicies: {
        ses: new iam.PolicyDocument({
          statements: [
            new iam.PolicyStatement({
              actions: [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents",
                "logs:DescribeLogGroups",
                "logs:DescribeLogStreams",
              ],
              resources: [vpcLogGroup.logGroupArn],
              effect: iam.Effect.ALLOW,
            }),
          ],
        }),
      },
    });

    // Create VPC Flow Log
    new ec2.CfnFlowLog(this, "FlowLogs", {
      resourceId: vpc.vpcId,
      resourceType: "VPC",
      trafficType: "ALL",
      deliverLogsPermissionArn: vpcFlowRole.roleArn,
      logDestinationType: "cloud-watch-logs",
      logGroupName: vpcLogGroup.logGroupName,
    });

    const cluster = new ecs.Cluster(this, "MultiImageCluster", {
      vpc: vpc,
      clusterName: `${this.PREFIX}-cluster`,
    });

    const deployService = async (service: ServicePort) => {
      const serviceRepo = ecr.Repository.fromRepositoryName(
        this,
        `${service.name}-RepositoryService`,
        `${service.name}`
      );

      const task_definition = new ecs.FargateTaskDefinition(
        this,
        `${service.name}-Task-def`,
        {
          cpu: 256,
          memoryLimitMiB: 512,
          runtimePlatform: {
            operatingSystemFamily: ecs.OperatingSystemFamily.LINUX,
            cpuArchitecture: ecs.CpuArchitecture.X86_64,
          },
        }
      );

      const container = task_definition.addContainer(
        `${service.name}-container`,
        {
          image: ecs.ContainerImage.fromEcrRepository(serviceRepo, "latest"),
          logging: ecs.LogDrivers.awsLogs({
            streamPrefix: `${service.name}-stream`,
            logRetention: logs.RetentionDays.ONE_DAY,
          }),
        }
      );

      container.addPortMappings({
        containerPort: service.port,
        protocol: ecs.Protocol.TCP,
      });

      // Create a load-balanced Fargate service and make it public
      const fargateService =
        new ecs_patterns.ApplicationLoadBalancedFargateService(
          this,
          `${service.name}-fargateService`,
          {
            cluster: cluster, // Required
            cpu: 256, // can be >= 256
            serviceName: `${service.name}`,

            loadBalancerName: `${service.name}-ALB`,
            desiredCount: 2, // Default is 1
            taskDefinition: task_definition,

            listenerPort: 80,
            memoryLimitMiB: 512, // can be >= 512
            publicLoadBalancer: true, // can be set to false
          }
        );

      // Add Scaling
      const scaling = fargateService.service.autoScaleTaskCount({
        maxCapacity: 5,
        minCapacity: 1,
      });
      scaling.scaleOnCpuUtilization("CpuScaling", {
        targetUtilizationPercent: 70,
      }); // default cooldown of 5 min
      scaling.scaleOnMemoryUtilization("RamScaling", {
        targetUtilizationPercent: 70,
      }); // default cooldown of 5 min

      fargateService.targetGroup.configureHealthCheck({
        path: "/",
      });

      const httpApi = new apigw2.HttpApi(this, `${service.name}-HttpApi`, {
        apiName: `${service.name}-api`,
      });

      httpApi.addRoutes({
        path: "/",
        methods: [apigw2.HttpMethod.GET],
        integration: new HttpAlbIntegration(
          `${service.name}-AlbIntegration`,
          fargateService.listener
        ),
      });
    };

    const deployAllServices = async () => {
      for (const service of servicesPorts) {
        await deployService(service);
      }
    };

    deployAllServices();
  }
}
