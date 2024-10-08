import os

from fastapi import FastAPI

import logging

from pydantic import BaseModel

app = FastAPI()
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

@app.get('/')
def health_check():
    return {"Health is Ok"}

@app.post('/v1.0/subscribe/packages/pickup')
def receive_package_pickup_event(event: CloudEvent):
    logging.info(f'Notification event: %s:' % {event.data['package_model']})
    print(f'notification service: {event}')
    return {'success': True}


@app.post('/v1.0/subscribe/packages/drop-off')
def package_drop_off_event(event: CloudEvent):
    logging.info(f'delivery status update event id: %s:' % event.data['id'])
    print(f'notification service: {event}')
    return {'success': True}


@app.post('/v1.0/subscribe/packages/assign')
def receive_assign_package_request(event: CloudEvent):
    logging.info(f'Notification event: %s:' % {event.data['package_model']})
    print(f'notification service: {event}')
    return {'success': True}


@app.post('/v1.0/subscribe/packages/delivery-status')
def receive_delivery_status_request(event: CloudEvent):
    logging.info(f'Notification event: %s:' % event.model_dump_json())
    print(f'notification service: {event}')
    return {'success': True}
@app.post('/v1.0/subscribe/users/account-created')
def delivery_user_account_created(event: CloudEvent):
    logging.info(f'Notification event: %s:' % event.data)
    print(f'notification service: {event}')
    return {'success': True}

