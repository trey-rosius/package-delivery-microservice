import grpc
import json

from dapr.clients import DaprClient
from fastapi import FastAPI
import logging

import os

from fastapi import HTTPException
from models.user_model import UserModel

user_db = os.getenv('DAPR_USER_DB', 'userdb')

app = FastAPI()

logging.basicConfig(level=logging.INFO)


@app.post('v1.0/state/users')
def create_user_account(user_model: UserModel) -> UserModel:
    with DaprClient() as d:
        print(f"User={user_model.model_dump()}")
        try:
            d.save_state(store_name=user_db,
                         key=str(user_model.id),
                         value=user_model.model_dump_json())
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


@app.get('/v1.0/invoke/users/{user_id}')
def invoke_get_user_account(user_id: str):
    with DaprClient() as d:
        try:
            kv = d.get_state(user_db, user_id)
            user_account = UserModel(**json.loads(kv.data))

            return user_account.model_dump()
        except grpc.RpcError as err:
            print(f"Error={err.details()}")
            raise HTTPException(status_code=500, detail=err.details())

# listen for cloud events (UPDATE_DELIVERY_AGENT_STATUS)
@app.post('/v1.0/subscribe/packages/assign')
def update_delivery_agent_status(user_id: str,status:str):
    with DaprClient() as d:
        try:
            kv = d.get_state(user_db, user_id)
            user_account = UserModel(**json.loads(kv.data))
            user_account.delivery_agent_status = status

            d.save_state(store_name=user_db,
                         key=str(user_account.id),
                         value=user_account.model_dump_json())

            return {"message":"Delivery agent status updated successfully"}
        except grpc.RpcError as err:
            print(f"Error={err.details()}")
            raise HTTPException(status_code=500, detail=err.details())


@app.post('/v1.0/state/users/{user_id}')
def delete_user_account(user_id: str):
    with DaprClient() as d:
        try:
            d.delete_state(user_db, user_id)

            return {"message": "User deleted"}

        except grpc.RpcError as err:
            print(f"Error={err.details()}")
            raise HTTPException(status_code=500, detail=err.details())
