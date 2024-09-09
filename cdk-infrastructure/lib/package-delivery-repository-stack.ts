import * as cdk from "aws-cdk-lib";
import { Construct } from "constructs";
import * as ecr from "aws-cdk-lib/aws-ecr";
import * as fs from "fs";
import * as path from "path";
export class PackageDeliveryRepositoryStack extends cdk.Stack {
  repository: ecr.Repository;

  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Define the path to the services directory
    const servicesDir = path.join(__dirname, "../../services");

    // Read the services directory to get a list of service names
    const services = fs
      .readdirSync(servicesDir)
      .filter((file) =>
        fs.statSync(path.join(servicesDir, file)).isDirectory()
      );

    services.forEach((service) => {
      new ecr.Repository(this, `${service}Repository`, {
        repositoryName: service.toLowerCase(), // ECR repository names must be lowercase
        removalPolicy: cdk.RemovalPolicy.DESTROY, // Automatically delete the repo when the stack is deleted
      });
    });
  }
}
