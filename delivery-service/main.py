import json
import os

from dapr.clients import DaprClient
from fastapi import FastAPI, HTTPException
from models.delivery_status_model import DeliveryStatusModel

import grpc

import logging

from pydantic import BaseModel

app = FastAPI()
delivery_db = os.getenv('DAPR_DELIVERIES_COLLECTION', '')
del_status_update_topic_name = os.getenv('DAPR_DELIVERY_STATUS_UPDATE_TOPIC_NAME', '')
package_drop_off_topic_name = os.getenv('DAPR_PACKAGE_DROP_OFF_TOPIC_NAME', '')
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


@app.post('/v1.0/publish/delivery-service/drop-off')
def package_drop_off(delivery_status_model: DeliveryStatusModel):
    with DaprClient() as d:
        logging.info(f'package id is:{delivery_status_model.packageId}')

        try:

            d.save_state(store_name=delivery_db,
                         key=delivery_status_model.packageId,
                         value=delivery_status_model.model_dump_json(),
                         state_metadata={"contentType": "application/json"})
            delivery_data = {
                "id": delivery_status_model.packageId
            }

            d.publish_event(
                pubsub_name=pubsub_name,
                topic_name=package_drop_off_topic_name,
                data=json.dumps(delivery_data),
                data_content_type='application/json',
            )

            return delivery_status_model.model_dump()
        except grpc.RpcError as err:
            print(f"Error={err.details()}")
            raise HTTPException(status_code=500, detail=err.details())

@app.post('/v1.0/publish/delivery-service/movement')
def delivery_status_update(delivery_status_model: DeliveryStatusModel):
    with DaprClient() as d:
        logging.info(f'package id is:{delivery_status_model.packageId}')

        try:

            d.save_state(store_name=delivery_db,
                         key=delivery_status_model.packageId,
                         value=delivery_status_model.model_dump_json(),
                         state_metadata={"contentType": "application/json"})
            delivery_data = {
                "id": delivery_status_model.packageId
            }

            d.publish_event(
                pubsub_name=pubsub_name,
                topic_name=del_status_update_topic_name,
                data=json.dumps(delivery_data),
                data_content_type='application/json',
            )

            return delivery_status_model.model_dump()
        except grpc.RpcError as err:
            print(f"Error={err.details()}")
            raise HTTPException(status_code=500, detail=err.details())

