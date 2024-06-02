# Building Serverless Microservices with Dapr and Catalyst

# Building reliable and fault tolerant distributed applications with Dapr and Diagrid Catalyst.

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

> N.B
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
