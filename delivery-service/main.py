import os

from dapr.clients import DaprClient
from fastapi import FastAPI, HTTPException

import grpc

import logging

from pydantic import BaseModel

app = FastAPI()
delivery_db = os.getenv('DAPR_DELIVERIES_COLLECTION', '')
pubsub_name = os.getenv('DAPR_PUB_SUB', 'awssqs')
logging.basicConfig(level=logging.INFO)


class CloudEvent(BaseModel):
    datacontenttype: str
    source: str
    topic: str
    pubsubname: str
    data: dict
    id: str
    specversion: str
    tracestate: str
    type: str
    traceid: str


@app.post('/api/v1/delivery-service/{package_id}')
def delivery_status_update(package_id: str):

    with DaprClient() as d:
        logging.info(f'package id is:{package_id}')

        try:
            delivery_package = {

            }
            d.save_state(store_name=delivery_db,
                         key=package_id,
                         value=package_model.model_dump_json())

            return {"message": "package successfully created"}
        except grpc.RpcError as err:
            print(f"Error={err.details()}")
            raise HTTPException(status_code=500, detail=err.details())



    return {'success': True}

