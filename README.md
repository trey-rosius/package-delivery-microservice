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

### Configure State

For state management, we'll use MongoDB.
If you don't have a mongo db account yet, please follow this link to create one and also create a mongo db serverless instance. I'll show you how to do that below.

https://mongodb.com/

### Creating a MongoDB Serverless Instance

Once you've created a mongo db account, create a new project with any name of your choice. I'll name mine `package_delivery`.

Once created, click on the project name and proceed to the next screen(`Clusters`).

On the far right corner of the `Clusters` screen, click on `Create` to create a new cluster. See screenshot below.

![create-cluster](https://raw.githubusercontent.com/trey-rosius/package-delivery-microservice/master/assets/create.png)

Inside the `create cluster screen` click on the serverless tab.

![serverless-cluster](https://raw.githubusercontent.com/trey-rosius/package-delivery-microservice/master/assets/serverless_cluster.png)

Next, give your instance a familiar name and then click on `Create Instance`.

![serverless-instance](https://raw.githubusercontent.com/trey-rosius/package-delivery-microservice/master/assets/instance_name.png)

Bear in mind that you can also choose to use a shared free instance for this workshop. I used a serverless instance because i had already ran out of the free tier.

## Secure the database with a username and password

The next step is to create a username and password with administrative access to the instance we created above.

Under the `Security` tab, click on `Database access` and create a new

![add-new-db-user](https://raw.githubusercontent.com/trey-rosius/package-delivery-microservice/master/assets/add_new_db_user.png)

Add Password

![add-password](https://raw.githubusercontent.com/trey-rosius/package-delivery-microservice/master/assets/add_password.png)

Select User Role.

![add-password](https://raw.githubusercontent.com/trey-rosius/package-delivery-microservice/master/assets/select_role.png)

Take note of your database `username` and `password`. We'll be needed them when creating a state connection in Catalyst.

## Microservices

For this application, we'll have 5 services, each of which corresponds to a Catalyst `App ID` as illustrated in the image below.

![catalyst_app_ids](https://raw.githubusercontent.com/trey-rosius/package-delivery-microservice/master/assets/catalyst_app_id.png)

You can read more about Catalyst Application Identities here
https://docs.diagrid.io/catalyst/concepts/appids

## User Service

### Introduction

Responsible for handling User Account functionalities such as creating/updating/reading/deleting user information.

This service is also responsible for invoking requests and sending/receiving events such as

- Delivery user account created event
- User deleted Event
- Update delivery agent status event

### Solutions Architecture for this service

![user_service_architecture](https://raw.githubusercontent.com/trey-rosius/package-delivery-microservice/master/assets/user_service_architecture.png)

## Get Started

### Create User-Service app id

From the Catalyst Interface,click on `Create App ID`. Name your app Id `user-service`.

![create_app_id](https://raw.githubusercontent.com/trey-rosius/package-delivery-microservice/master/assets/create_app_id.png)

Once created navigate the connections screen. Let's add a state management connection for this `user-service`.

### Create `userdb` connection

From the `Connection` screen, click on `Create Connection`. Select `state` as the connection type.

![conn_type](https://raw.githubusercontent.com/trey-rosius/package-delivery-microservice/master/assets/conn_type.png)

Select `MongoDB` as the connection.

![conn](https://raw.githubusercontent.com/trey-rosius/package-delivery-microservice/master/assets/conn.png)

Assign Access to your `user-service` app id you created above.

![assign_access](https://raw.githubusercontent.com/trey-rosius/package-delivery-microservice/master/assets/assign_access.png)

In the authentication profile tab, select username and password

![username_password](https://raw.githubusercontent.com/trey-rosius/package-delivery-microservice/master/assets/username_password.png)
