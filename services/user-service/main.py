import grpc
import json

from dapr.clients import DaprClient
from fastapi import FastAPI, HTTPException
import logging
import os
from models.user_model import UserModel, UserType, DELIVER_AGENT_STATUS, PaymentModel

user_db = os.getenv('DAPR_USER_DB', '')
pubsub_name = os.getenv('DAPR_PUB_SUB', '')
delivery_agent_account_created_topic = os.getenv('DAPR_DELIVER_AGENT_ACCOUNT_CREATED_TOPIC_NAME', '')
user_deleted_topic_name = os.getenv('DAPR_USER_ACCOUNT_DELETED_TOPIC_NAME', '')

app = FastAPI()

logging.basicConfig(level=logging.INFO)


@app.post('/v1.0/state/users')
def create_user_account(user_model: UserModel) -> UserModel:
    with DaprClient() as d:
        print(f"User={user_model.model_dump()}")
        try:
            d.save_state(store_name=user_db,
                         key=str(user_model.id),
                         value=user_model.model_dump_json(),
                         state_metadata={"contentType": "application/json"})

            if user_model.user_type == UserType.DELIVERY_AGENT:
                d.publish_event(
                    pubsub_name=pubsub_name,
                    topic_name=delivery_agent_account_created_topic,
                    data=user_model.model_dump_json(),
                    data_content_type='application/json', )
                return user_model
            else:
                return user_model

        except grpc.RpcError as err:
            print(f"Error={err.details()}")
            raise HTTPException(status_code=500, detail=err.details())


@app.get('/v1.0/state/users/{user_id}')
def get_user_account(user_id: str):
    with DaprClient() as d:
        try:
            kv = d.get_state(user_db, user_id)
            user_account = UserModel(**json.loads(kv.data))

            return user_account.model_dump()
        except grpc.RpcError as err:
            print(f"Error={err.details()}")
            raise HTTPException(status_code=500, detail=err.details())


@app.get('/v1.0/state/users/type/{user_type}')
def get_users_by_status(user_type: str):
    with DaprClient() as d:
        try:
            users = []

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

            kv = d.query_state(

                store_name=user_db,
                query=query_filter

            )
            print(f"packages are {kv}")

            for item in kv.results:
                user_model = UserModel(**json.loads(item.value))
                users.append(user_model)
                print(f"free delivery agents {user_model.model_dump()}")

            return users
        except grpc.RpcError as err:
            print(f"Error={err.details()}")
            raise HTTPException(status_code=500, detail=err.details())


@app.get('/v1.0/invoke/users')
def get_a_free_delivery_agent():
    with DaprClient() as d:
        try:
            users = []

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

            kv = d.query_state(

                store_name=user_db,
                query=query_filter

            )

            for item in kv.results:
                user_model = UserModel(**json.loads(item.value))
                users.append(user_model)
                print(f"Users {user_model.model_dump()}")

            return users
        except grpc.RpcError as err:
            print(f"Error={err.details()}")
            raise HTTPException(status_code=500, detail=err.details())


# listen for cloud events (UPDATE_DELIVERY_AGENT_STATUS)
@app.post('/v1.0/subscribe/packages/assign')
def update_delivery_agent_status(user_id: str, status: str):
    with DaprClient() as d:
        try:
            kv = d.get_state(user_db, user_id)
            user_account = UserModel(**json.loads(kv.data))
            user_account.delivery_agent_status = status

            d.save_state(store_name=user_db,
                         key=str(user_account.id),
                         value=user_account.model_dump_json(),
                         state_metadata={"contentType": "application/json"})

            return {"message": "Delivery agent status updated successfully"}
        except grpc.RpcError as err:
            print(f"Error={err.details()}")
            raise HTTPException(status_code=500, detail=err.details())


@app.delete('/v1.0/state/users/{user_id}')
def delete_user_account(user_id: str):
    with DaprClient() as d:
        try:
            kv = d.get_state(user_db, user_id)
            user_account = UserModel(**json.loads(kv.data))
            user_account.is_active = False

            d.save_state(store_name=user_db,
                         key=str(user_account.id),
                         value=user_account.model_dump_json(),
                         state_metadata={"contentType": "application/json"})

            return {"message": "User account deleted successfully"}

        except grpc.RpcError as err:
            print(f"Error={err.details()}")
            raise HTTPException(status_code=500, detail=err.details())


