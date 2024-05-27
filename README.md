# Building Serverless Microservices with Dapr and Catalyst

# Building Serverless Distributed Applications with DAPR CATALYST

In this workshop, we'll be looking at how to build a serverless microservice api for a package delivery service using the Dapr Catalyst API.
Catalyst helps you abstract away the complexities of building microservice architectures, by providing unified APIs for messaging, data and workflows, powered by open-source Dapr.

Here's a high level overview of the application's architecture.

![high-level-overview](https://raw.githubusercontent.com/trey-rosius/package-delivery-microservice/master/assets/hlo1.png)

## Prerequisites And Assumptions

Before proceeding, please ensure that you have these prerequisites installed on your computer.

- Python 3.8+(Python 3.10 is preferable)
- Vscode or Pycharm(Preferably)

### Installing Diagrid Catalyst

```bash
# Install Dapr client SDK
pip3 install dapr

# Install Dapr gRPC AppCallback service extension
pip3 install dapr-ext-grpc

```

Please find more installation instructions here [diagrid-catalyst](https://docs.diagrid.io/catalyst/how-to-guides/connect-from-sdks)

## Microservices

For this application, we'll have 5 services, each of which corresponds to a Catalyst `App ID` as illustrated in the image below.

![catalyst_app_ids](https://raw.githubusercontent.com/trey-rosius/package-delivery-microservice/master/assets/catalyst_app_id.png)

## User Service

### Introduction

Responsible for handling User Account functionalities such as creating/updating/reading/deleting user information.

This service is also responsible for invoking requests and sending/receiving events. Such as

- Delivery user account created event
- User deleted Event
- Update delivery agent status event

### Solutions Architecture for this service

![user_service_architecture](https://raw.githubusercontent.com/trey-rosius/package-delivery-microservice/master/assets/user_service_architecture.png)

## Get Started
