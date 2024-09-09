#!/usr/bin/env node
import "source-map-support/register";
import * as cdk from "aws-cdk-lib";
import {PackageDeliveryMicroserviceStack} from "../lib/package-delivery-microservice-stack";
import { PackageDeliveryRepositoryStack } from "../lib/package-delivery-repository-stack";

const app = new cdk.App();

new PackageDeliveryRepositoryStack(app, "PackageDeliverRepositoryStack", {});
new PackageDeliveryMicroserviceStack(app, "PackageDeliveryMicroserviceStack", {});
