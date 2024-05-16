import os

from dapr.clients import DaprClient
from fastapi import FastAPI, HTTPException

import grpc

import logging

from pydantic import BaseModel

app = FastAPI()
package_db = os.getenv('DAPR_PACKAGES_DB', 'packagesdb')
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

@app.post('/api/pickup')
def receive_package_pickup_event(event:CloudEvent):
    logging.info(f'Notification event: %s:' % {event.data['package_model']})
    print(f'notification service: {event}')
    return {'success':True}



