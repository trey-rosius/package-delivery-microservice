import os

from dapr.clients import DaprClient
from fastapi import FastAPI, HTTPException
from models.delivery_status_model import DeliveryStatusModel

import grpc

import logging

from pydantic import BaseModel

app = FastAPI()
delivery_db = os.getenv('DAPR_DELIVERIES_COLLECTION', '')
topic_name = os.getenv('DAPR_DELIVERY_STATUS_UPDATE_TOPIC_NAME', '')
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


@app.post('/api/v1/delivery-service/update-package-status')
def delivery_status_update(delivery_status_model: DeliveryStatusModel):

    with DaprClient() as d:
        logging.info(f'package id is:{delivery_status_model.packageId}')

        try:

            d.save_state(store_name=delivery_db,
                         key=delivery_status_model.packageId,
                         value=delivery_status_model.model_dump_json())

            d.publish_event(
                pubsub_name=pubsub_name,
                topic_name=topic_name,
                data=delivery_status_model.model_dump_json(),
                data_content_type='application/json',
            )

            return {"message": "delivery status updated successfully created"}
        except grpc.RpcError as err:
            print(f"Error={err.details()}")
            raise HTTPException(status_code=500, detail=err.details())



    return {'success': True}

