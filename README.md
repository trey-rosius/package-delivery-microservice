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

## Create a Diagrid Catalyst application

From your CLI, login to diagrid Catalyst using the following command

`diagrid login `

Then Confirm your login was successful

`diagrid whoami`

### Create a Diagrid project

```bash
diagrid project create package-delivery-project
```

To set this project as the default project in the Diagrid CLI, run:

```bash
diagrid project use package-delivery-project
```

Create a new python project in pycharm, and set python version of the `venv` environment to `3.10`.

The project should have a default `main.py` file and a `requirements.txt` file. Add those, if your project doesn't already have them.

Let's proceed to creating `app ids` and `states` before returning to scaffold our project.

## Package Delivery Microservices

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

Within your created project,from the Catalyst Interface,click on `Create App ID`. Name your app Id `user-service`.

![create_app_id](https://raw.githubusercontent.com/trey-rosius/package-delivery-microservice/master/assets/create_app_id.png)

Once created navigate the connections screen.

> N.B:
> You'll repeat the above steps when creating the other 4 microservices App IDs.

## State Management

Let's add a state management connection for this `user-service`.

### Create `usersdb` connection

From the `Connection` screen, click on `Create Connection`. Select `state` as the connection type.

![conn_type](https://raw.githubusercontent.com/trey-rosius/package-delivery-microservice/master/assets/conn_type.png)

Select `MongoDB` as the connection.

![conn](https://raw.githubusercontent.com/trey-rosius/package-delivery-microservice/master/assets/conn.png)

Assign Access to your `user-service` app id you created above.

![assign_access](https://raw.githubusercontent.com/trey-rosius/package-delivery-microservice/master/assets/assign_access.png)

In the authentication profile tab, select username and password

![username_password](https://raw.githubusercontent.com/trey-rosius/package-delivery-microservice/master/assets/username_password.png)

Enter the `username` and `password` you created in MongoDB to access this database.

Also, you'll have to add the server string and parameters.

![Mongo_connection](https://raw.githubusercontent.com/trey-rosius/package-delivery-microservice/master/assets/mongo_conn.png)

Sign into your MongoDB account and navigate to your instance.

Click on the green button which reads `Connect`.

![connect](https://raw.githubusercontent.com/trey-rosius/package-delivery-microservice/master/assets/connect.png)

In the next screen, click on `drivers`

![drivers](https://raw.githubusercontent.com/trey-rosius/package-delivery-microservice/master/assets/drivers.png)

Then copy the connection string.

![connection_string](https://raw.githubusercontent.com/trey-rosius/package-delivery-microservice/master/assets/conn_string.png)

In the next screen (Configure Connection), set Connection Name to `usersdb` or whatever you prefer and then add a collectionName = `users`.

![configure_connection](https://raw.githubusercontent.com/trey-rosius/package-delivery-microservice/master/assets/configure_connection.png)

Click on continue and save.

> N.B
> You'll replicate these same steps to create state management connections for `packagesdb` and `deliverydb` later on in this workshop.

## Pub/Sub Connection

Communication between services in our application will be done through events. For our use case, we'll be using AWS SQS/SNS as the message brokers for this application.

Log into your AWS application and create credentials for the AWS CLI.

Configure your CLI using the command

`aws configure`

and then passing in the ACCESS_KEY_ID and ACCESS_SECRET when asked.

Follow this visual guide incase you need assistance. [CREATE IAM USER](https://www.educloud.academy/content/aee6b0ae-fc22-45db-a497-4b70b4c4cd6e/eb3f129e-b9d7-499a-9467-bd4480a18c7c/598a522a-fd94-46a6-92b3-1d6f1d90ea28/)

Navigate to your Catalyst Console, click on connections, select `pubsub` as connection type and `AWS SNS/SQS` as Connection.

![configure_connection_pub_sub](https://raw.githubusercontent.com/trey-rosius/package-delivery-microservice/master/assets/pub_sub.png)

Click on Next.

Check the `Select All ` Checkbox because we want all our services to have access to this pub/sub.

Put in your access key id and secret and click continue.

![configure_connection_pub_sub](https://raw.githubusercontent.com/trey-rosius/package-delivery-microservice/master/assets/access_key_id.png)

Put in a connection name of your choice and region, i used `awssqs` and `us-east-1` as the name and region respectively.

![configure_connection_pub_sub](https://raw.githubusercontent.com/trey-rosius/package-delivery-microservice/master/assets/pub_sub_conn_name.png)

## Scaffold Diagrid Catalyst Project

Right now, we'll have to develop our application locally, while accessing the Catalyst API's.

The first step is to scaffold our project.

Assuming that the project we created and made the default above is still default, run the following command.

```bash

diagrid dev scaffold

```

This command produces the file dev-<project-name>.yaml containing the app connection details for all the App IDs in the current Catalyst project. The dev config file has the following format:

```yaml
project: <project-name> # Project that this file was generated from and connects to
apps: # List of App IDs in a project to run locally and/or create an app connection for
  - appId: <appid> # App ID name
    appPort: 0 # Optional: Port used by Catalyst to establish a local app connection to your code
    env: # App environment variables necessary for connecting to the Catalyst APIs
      DAPR_API_TOKEN: <appid-api-token>
      DAPR_APP_ID: <appid>
      DAPR_GRPC_ENDPOINT: <your-project-grpc-url>
      DAPR_HTTP_ENDPOINT: <your-project-http-url>
    workDir: <> # Work directory to run the start-up command in
    command: [] # Start-up command to run the application
```

You can read more here https://docs.diagrid.io/catalyst/how-to-guides/develop-locally#run-multiple-with-diagrid-dev-cli

Inside your requirements.txt, add these dependencies.

```bash
dapr==1.13.0
fastapi==0.109.1
grpcio==1.62.0
pydantic==2.4.2
requests==2.31.0
uvicorn==0.23.2

```

Activate your python version environment using this command

MacOS/Linux

`source venv/bin/activate`

Windows

`venv/Scripts/activate.bat`

Then install the dependencies in the requirements.txt file.

`pip install -r requirements.txt`

Here's how my `dev-<project-name>.yaml` file looks like now.

Once successfully installed, run the diagrid dev state command.

```yaml
project: MY-PROJECT-NAME
apps:
  - appId: user-service
    appPort: 5001
    env:
      DAPR_API_TOKEN: DIAGRID_TOKEN
      DAPR_APP_ID: user-service
      DAPR_CLIENT_TIMEOUT_SECONDS: 10
      DAPR_USER_DB: usersdb
      DAPR_GRPC_ENDPOINT: DIAGRID_GRPC_ENDPOINT
      DAPR_HTTP_ENDPOINT: DIAGRID_HTTP_ENDPOINT
    workDir: user-service
    command:
      - uvicorn
      - main:app
      - --port
      - "5001"
```

`diagrdi dev start -f dev-<project-name>.yaml`

This command starts all diagrid app ids in your project.
At this point, we only have the user-service app ID. We'll add more app ids as we progress through the workshop.

Also, bear in mind that each app id represents a service within our microservice api.

- Each service has to be independently deployable.
- Communication between services have to be done over clearly defined API's and Events.
- Services within the microservice have to be isolated and decoupled.

In order to adhere to the above microservices standards, we'll use Docker to build and deploy our microservices in a consistent and isolated manner to AWS Apprunner.

Docker has a ton of advantanges, which makes it a good choice for this use case.
