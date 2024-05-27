# Building Serverless Microservices with Dapr and Catalyst

# Building Serverless Distributed Applications with DAPR CATALYST

In this workshop, we'll be looking at how to build a serverless microservice api for a package delivery service using the Dapr Catalyst API.
Catalyst helps you abstract away the complexities of building microservice architectures, by providing unified APIs for messaging, data and workflows, powered by open-source Dapr.

Here's a high level overview of the application's architecture.

![high-level-overview](../package-delivery-microservice/assets/hlo1.png)
api's.

## Microservices

For this microservice api, we'll have 5 services, each of which corresponds to a Catalysts `App ID` as illustrated in the image below.

![catalyst_app_ids](../)

- User Service
- Package Service
- Pickup Service
- Delivery Service
- Notification Service
