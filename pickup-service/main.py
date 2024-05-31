import json
import os

from dapr.clients import DaprClient
from fastapi import FastAPI, HTTPException
import requests
import grpc
from models.cloud_events import CloudEvent
import logging

app = FastAPI()
base_url = os.getenv('DAPR_HTTP_ENDPOINT', 'http://localhost')
pubsub_name = os.getenv('DAPR_PUB_SUB', '')
target_app_id = os.getenv('DAPR_TARGET_APP_ID', '')
target_api_token = os.getenv('DAPR_TARGET_API_TOKEN', '')
topic_name = os.getenv('DAPR_ASSIGN_PACKAGE_REQUEST_TOPIC_NAME', '')
logging.basicConfig(level=logging.INFO)


@app.post('/v1.0/subscribe/packages/pickup')
async def pickup_package_event(event: CloudEvent):
    with DaprClient() as d:
        logging.info(f'Received event: %s:' % {event.model_dump_json()})
        logging.info(f'Received event: %s:' % {event.data['package_model']})

        package_model = json.loads(event.data['package_model'])

        # assign package to available delivery guy.
        headers = {'dapr-app-id': target_app_id, 'dapr-api-token': target_api_token,
                   'content-type': 'application/json'}
        try:
            result = requests.get(
                url='%s/v1.0/invoke/users' % base_url,
                headers=headers
            )

            if result.ok:
                logging.info('Invocation successful with status code: %s' %
                             result.status_code)
                print("result is %s" % result.json())
                driver_details = result.json()

                package_model['deliveryAgentId'] = driver_details[0]['id']
                package_model['packageStatus'] = "ASSIGNED"

                package_details = {
                    "package_model": json.dumps(package_model),
                    "event_type": "assignPackageRequest"
                }

                d.publish_event(
                    pubsub_name=pubsub_name,
                    topic_name=topic_name,
                    data=json.dumps(package_details),
                    data_content_type='application/json',
                )

                return result.json()

            else:
                logging.error(
                    'Error occurred while invoking App ID: %s' % result.reason)
                raise HTTPException(status_code=500, detail=result.reason)

        except grpc.RpcError as err:
            logging.error(f"ErrorCode={err.code()}")
            raise HTTPException(status_code=500, detail=err.details())
