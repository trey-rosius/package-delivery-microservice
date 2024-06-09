## Package Delivery Service API

This project is a Free to Use and Open Source under the MIT license, made in accordance with these [rules](https://22146261.fs1.hubspotusercontent-na1.net/hubfs/22146261/Catalyst%20Hackathon/Diagrid%20Catalyst%20AWS%20Hackathon%20Rules.docx.pdf).

It's a submission for the [Diagrid AWS Hackathon](https://www.diagrid.io/blog/innovate-and-win-its-the-diagrid-catalyst-aws-hackathon)

## Project Overview

### Problem Statement

Covid came and went. This led to a huge lifestyle change in both individuals and organizations. Ordering stuff especially food, from home was and still is the norm.

Where i live,the concept of online delivery is still a thing of the past. It's incredibly difficult to reliably order stuff online and have it delivered to you without a ton of back and forth.

One of the main difficulty is the unknown wait times. You place an order, give your address and then pray to God. Because 7 times out of 10, the delivery agent gets your location mixed up and delivers your food elsewhere.

Most times, they have to do soo many deliveries that your food gets cold before it arrives.

You get zero observability into what location your food and delivery agent are exactly. How much time you have to wait or how long it'll take for the food to arrive.

The entire system is like most serverless apps. A black box. Zero insights into the system's internal functionality.

You just have to sit and pray everything goes smoothly and your meal arrives.

Don't get me started with "sending packages across the city".

## Proposed Proof of Concept

In this workshop, we'll be looking at how to build a serverless microservice api for a realtime package delivery service using Diagrid's Catalyst API.

Catalyst helps you abstract away the complexities of building microservice architectures, by providing unified APIs for messaging, data and workflows, powered by open-source [Dapr](https://dapr.io/).

For Application decoupling and isolation, we will use AWS SQS/SNS as a message broker and MongoDB for state management. Both of which are supported by the Catalyst API's.

For synchronous communication between services, we will employ the Dapr request/response API, which will be elaborated on during the workshop.

Additionally, we will orchestrate payments within the API using Dapr Workflows.

Each microservice will correspond to a Catalyst App ID and will be independently deployed to AWS AppRunner using Docker and AWS Elastic Container Service (ECS).

Finally, we'll implement a Graphql API using AWS AppSync with JavaScript Resolvers, Cognito, and AWS WAF (Web Application Firewall).

This setup will unify all AppRunner endpoints, offering real-time capabilities, security, authorization, rate limiting, and throttling.

The working Graphql API and how to deploy it can be found [here](https://github.com/trey-rosius/cdk-package-delivery-microservice)

## Frontend Application

[Github](https://github.com/trey-rosius/Package-Delivery-Mobile-App)

I've built a barebones mobile application to visually illustrate how to consume the GraphQL endpoint. Also, I illustrate the realtime aspect of the api, by showing a location marker moving along a polyline, across a map.
Package location(longitude and latitude) updates are done every 5 seconds.

```
Destination location - Package location = Distance Left
```

Package Estimated time of arrival(ETA) can be calculated from Distance Left

https://github.com/trey-rosius/package-delivery-microservice/assets/29162353/de1bd1c6-e943-404c-b4de-3dc88d6a94fd

![high-level-overview](https://raw.githubusercontent.com/trey-rosius/Package-Delivery-Mobile-App/master/assets/images/package_details.png)

## Solutions architecture.

![high-level-overview](https://raw.githubusercontent.com/trey-rosius/package-delivery-microservice/master/assets/pds3.png)

## Project Description

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

Click on continue and save.

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
email-validator==2.1.1

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

# N.B

> The following sections would highlight code fragments(NOT THE COMPLETE CODE) used in creating different endpoints.

> Please access the complete code on the github directory.

> You'll also be required to do a couple of exercises throughout this workshop session. Don't worry, the exercises will only involve stuff we've previously covered.

## Creating Endpoints

We're going to be using [FastAPI](https://fastapi.tiangolo.com/) as the web application framework to build this API.

### Create User Account Endpoint

The first endpoint we'll create is the `createUserAccount` endpoint.

This endpoint takes in valid user inputs, saves them to the state(usersdb) and then published a `delivery_agent_account_created` event if the newly created account was for a `DELIVERY AGENT`.

We'll use pydantic for data validation.

Because our project is going to have many different services, we'll put one each of these services within a folder.

Create a folder called `user-service` and move the `main.py` and `requirements.txt` file into it.Create another folder called `models` within the `user-service` folder.

Create a python file called `user_model.py` inside the `models`. We'll define all our pydantic classes within this file.

Type the following code within this file.

```python

class UserModel(BaseModel):
    id: str
    email: EmailStr
    username: str
    first_name: str
    last_name: str
    address: Optional[Address]
    profile_pic_url: Optional[str]
    delivery_agent_status: Optional[DELIVER_AGENT_STATUS]
    geolocation: Geolocation
    is_active: bool
    is_admin: bool
    phone_number: str
    user_type: UserType
    created_at: int
    updated_at: Optional[int]


class UserType(str, Enum):
    CUSTOMER = "CUSTOMER"
    ADMIN = "ADMIN"
    DELIVERY_AGENT = "DELIVERY_AGENT"


class DELIVER_AGENT_STATUS(str, Enum):
    FREE="FREE"
    OCCUPIED="OCCUPIED"

class Address(BaseModel):
    street: str
    city: str
    zip: int
    country: str


class Geolocation(BaseModel):
    latitude: float
    longitude: float


```

Inside the `main.py` file, define the `POST` method for creating the user account and sending the event.

```py
@app.post('/v1.0/state/users')
def create_user_account(user_model: UserModel) -> UserModel:
    with DaprClient() as d:
        print(f"User={user_model.model_dump()}")
        try:
            #save user state
            d.save_state(store_name=user_db,
                         key=str(user_model.id),
                         value=user_model.model_dump_json(),
                         state_metadata={"contentType": "application/json"})

            # Only send event if created user is a delivery agent
            if user_model.user_type == UserType.DELIVERY_AGENT:
                d.publish_event(
                    pubsub_name=pubsub_name,
                    topic_name=delivery_agent_account_created_topic,
                    data=user_model.model_dump_json(),
                    data_content_type='application/json')
                return user_model
            else:
                return user_model

        except grpc.RpcError as err:
            print(f"Error={err.details()}")
            raise HTTPException(status_code=500, detail=err.details())
```

This event wouldn't publish, becuase we haven't created the subscription yet. Remember we created a pub/sub broker above. We need to add a producer and consumer to that broker.

The producer is our `user-service` and the consumber is a `notification-service` which we haven't also created.

## Exercise :

Create an app ID called `notification-service`. We did something similar above for the `user-service`.

## Create Subscription

When you're done, from your CLI, we'll create a subscription with the command below

```bash
diagrid subscription create delivery-agent-account-created -c awssqs -s notification-service -t delivery-agent-account-created -r  /v1.0/subscribe/users/account-created

```

- Topic name is `delivery-agent-account-created`
- Subscription name is `delivery-agent-account-created`
- subscription service is `notification service`
- Subscription endpoint is `/v1.0/subscribe/users/account-created`

![delivery_agent_sub](https://raw.githubusercontent.com/trey-rosius/package-delivery-microservice/master/assets/delivery_sub.png)

### Get User Account Endpoint

This endpoint retrieve a user's account using a `GET` request and the user's id.

```py
@app.get('/v1.0/state/users/{user_id}')
def get_user_account(user_id: str):
    with DaprClient() as d:
        try:
            # get user item state
            kv = d.get_state(user_db, user_id)
            user_account = UserModel(**json.loads(kv.data))

            return user_account.model_dump()
        except grpc.RpcError as err:
            print(f"Error={err.details()}")
            raise HTTPException(status_code=500, detail=err.details())

```

### Delete User Account

Deleting a user's account actually involves updating the `is_active` attribute in the user's model from `True` to `False`.
We won't be actually deleting user's details from the state.

```py
@app.delete('/v1.0/state/users/{user_id}')
def delete_user_account(user_id: str):
    with DaprClient() as d:
        try:
            # retrieve user account
            kv = d.get_state(user_db, user_id)
            user_account = UserModel(**json.loads(kv.data))

            # update attribute
            user_account.is_active = False

            # save state
            d.save_state(store_name=user_db,
                         key=str(user_account.id),
                         value=user_account.model_dump_json(),
                         state_metadata={"contentType": "application/json"})

            return {"message": "User account deleted successfully"}

        except grpc.RpcError as err:
            print(f"Error={err.details()}")
            raise HTTPException(status_code=500, detail=err.details())
```

### GET users by status

One of the use cases of this application is to be able to retrieve user's of a particular type. Say retrieve all `CUSTOMERS` OR `DELIVERY AGENTS` OR `ADMINS`.

This is a great use case for queries and thankfully, Dapr Queries support MONGODB which we're using.

Here's how our query looks like

```py
   query_filter = json.dumps({
                "filter": {
                    "AND": [
                        {
                            "EQ": {"is_active": True}
                        },
                        {
                            "EQ": {"user_type": user_type}
                        }

                    ]
                },
                "sort": [
                    {
                        "key": "id",
                        "order": "DESC"
                    }
                ],
                "page": {
                    "limit": 10
                }
            })

```

First, we want to make sure we're only retrieving active users, then we pass in the user type(e.g CUSTOMER).

We're getting 10 results back at a time. So we set the page limit to 10. If more than 10 records are available, the query returns with a token to get the next 10 results.

We'll pass in this query into the `query_state` method and get the output

```py
 kv = d.query_state(

                store_name=user_db,
                query=query_filter

            )

            for item in kv.results:
                user_model = UserModel(**json.loads(item.value))
                users.append(user_model)
                print(f"users {user_model.model_dump()}")

            return users
```

### GET a free Delivery Agent

This method will be invoked by the `pickup-service` which we haven't created yet. But we can talk about. In order for a delivery agent to be assigned to a deliver a package, they must be `FREE` at that point in time.

Using Diagrid's `Request/Reply` API, we'll synchronously invoke an endpoint inside the `user-service` that'll search and return 1 delivery agent with current delivery status as `FREE`.

Let's define the query filter for this endpoint.

```py
query_filter = json.dumps({
                "filter": {
                    "AND": [
                        {
                            "EQ": {"is_active": True}
                        },
                        {
                            "EQ": {"user_type": UserType.DELIVERY_AGENT}
                        },
                        {
                            "EQ": {"delivery_agent_status": DELIVER_AGENT_STATUS.FREE}
                        }

                    ]
                },
                "sort": [
                    {
                        "key": "id",
                        "order": "DESC"
                    }
                ],
                "page": {
                    "limit": 1
                }
            })
```

Firstly, we want to make sure the user is active, with a type of DELIVERY_AGENT and a `FREE` STATUS. All these conditions have to be true for this query to be successful.

Since we only need a single delivery person, we set the page limit to 1.

Then we use the `query_state` method

```py
 kv = d.query_state(

                store_name=user_db,
                query=query_filter

            )


            for item in kv.results:
                user_model = UserModel(**json.loads(item.value))
                users.append(user_model)
                print(f"free delivery agent {user_model.model_dump()}")
```

Get the complete code for the `user-service` from the github repo, run the application and test each endpoint.

We'll be looking at how to test each endpoint at the end of this workshop.

The next service we'll create is the `package-service`.

## Package Service

The Package Service is responsible for all package activities within the system such as

1. Creating a new package

2. Updating Package Status

3. Deleting a Package

4. Retrieving packages based on certain criteria, such as all packages per user or based on package status and a lot more.

5. Publishing package-pickup-requests events

6. Subscribing to package-drop-off events

7. Subscribing to package-status-update events

8. Subscribing to assign-package-request events

We'll start by creating an app ID called `package-service`. You can either use the Catalyst UI as we did above or run this CLI command.

`diagrid appid create package-service`

The next step is to create the package pickup event. This event simply notifies subscribers of the fact that, a package needs to be picked up and assigned a delivery agent.

We'll look more into the consequence of this event, when we'll be talking about the `pickup-service`.

Run the following command to create `package-pickup-event` with attached subscribers that happen to be the `notification-service` and `pickup-service`.

Create those app ids, if you haven't already done so.

```bash
diagrid subscription create package-pickup-request -c awssqs -s notification-service,pickup-service -t package-pickup-request -r /v1.0/subscribe/packages/pickup
```

Now, we have to add the `package-service` configuration into our `dev-<project-name>.yaml` file.

Currently, my `dev-<project-name>.yaml` file looks like this

```yaml
project: kv-project-fbe8f200-4
apps:
  - appId: package-service
    appPort: 5002
    env:
      DAPR_API_TOKEN: <TOKEN>
      DAPR_APP_ID: package-service
      DAPR_PACKAGES_DB: packagesdb
      DAPR_PUB_SUB: awssqs
      DAPR_CLIENT_TIMEOUT_SECONDS: 10
      DAPR_PACKAGE_PICKUP_TOPIC_NAME: package-pickup-request
      DAPR_GRPC_ENDPOINT: <ENDPOINT>
      DAPR_HTTP_ENDPOINT: <ENDPOINT>
    workDir: package-service
    command:
      - uvicorn
      - main:app
      - --port
      - "5002"

  - appId: user-service
    appPort: 5001
    env:
      DAPR_API_TOKEN: <TOKEN>
      DAPR_APP_ID: user-service
      DAPR_CLIENT_TIMEOUT_SECONDS: 10
      DAPR_USER_DB: usersdb
      DAPR_PUB_SUB: awssqs
      DAPR_DELIVER_AGENT_ACCOUNT_CREATED_TOPIC_NAME: delivery-agent-account-created
      DAPR_GRPC_ENDPOINT: <ENDPOINT>
      DAPR_HTTP_ENDPOINT: <ENDPOINT>
    workDir: user-service
    command:
      - uvicorn
      - main:app
      - --port
      - "5001"
```

The `package-service` app is listening on port `5002`. The `user-service` app was listening on port `5001`.

Create another folder within your project and name it `package-service`. So now there's the `user-service` folder and a `package-service` folder in your project folder.

Within the `package-service` folder, create a folder called `models`.

Create a `package_model.py` file within the models folder.

This file contains the package model class with package fields.

```py
class PackageModel(BaseModel):
    id: str
    packageName: str
    packageDescription: str
    pickupAddress: TransactionAddress
    deliveryAddress: TransactionAddress
    packageStatus: PackageStatus
    packageType: PackageType
    deliveryMode: PackageDeliveryMode
    senderId: str
    deliveryAgentId: Optional[str] = None
    createdAt: int
    updatedAt: Optional[int] =None
```

As mentioned above, get the complete code from the github repository.

### Create Package Endpoint

This endpoint grabs package inputs and saves them to the `packagesdb` state.

```py
@app.post('/v1.0/state/packages')
def create_package(package_model: PackageModel):
    with DaprClient() as d:
        print(f"package={package_model.model_dump()}")
        try:
            d.save_state(store_name=package_db,
                         key=str(package_model.id),
                         value=package_model.model_dump_json(),
                         state_metadata={"contentType": "application/json"})

            return package_model
        except grpc.RpcError as err:
            print(f"Error={err.details()}")
            raise HTTPException(status_code=500, detail=err.details())
```

In another variation of such an application, you might want to publish a `package-created` event and do something with the information. But for this workshop, we won't do that.

## Exercise

To test your knowledge and understanding of everything we've covered so far, write endpoints for

- get package(`@app.get('/v1.0/state/packages/{package_id}')`)
- Get all user packages(`@app.get('/v1.0/state/packages/users/{user_id}')`). For this endpoint, use a query with `senderId` equal to `user_id`
- Get Packages by package status(`@app.get('/v1.0/state/packages/status/{package_status}')`)

### Package Pickup Endpoint

`@app.get('/v1.0/publish/packages/send/{package_id}')`
This endpoint is executed when a user demands their package be picked up by a delivery agent.
Inside this funciton, 3 things happen.

1. Firstly, we get the package id and retrieve the entire package item

```py
   kv = d.get_state(package_db, package_id)
   package_model = PackageModel(**json.loads(kv.data))
```

2. Secondly, we update the package status from `PENDING` to `PICK_UP_REQUEST` and save.

```py
  # update package status
            package_model.packageStatus = PackageStatus.PICK_UP_REQUEST

            d.save_state(store_name=package_db,
                         key=str(package_model.id),
                         value=package_model.model_dump_json(),
                         state_metadata={"contentType": "application/json"})
```

3. Finally, we publish a `package-pickup-request` event.

```py
            package_details = {
                "package_model": package_model.model_dump_json(),
                "event_type": "package-pickup-request"
            }

            d.publish_event(
                pubsub_name=pubsub_name,
                topic_name=topic_name,
                data=json.dumps(package_details),
                data_content_type='application/json',
            )
```

If you notice, we could easily use a workflow to orchestrate these activities.

Maybe you'll love to redo this endpoint as a workflow as an exercise.

## Pickup Service

The next service is the pickup service
