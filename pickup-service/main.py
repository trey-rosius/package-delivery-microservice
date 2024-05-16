import json
import os

from dapr.clients import DaprClient
from fastapi import FastAPI, HTTPException
import requests
import grpc
from models.cloud_events import CloudEvent
import logging

from pydantic import BaseModel

app = FastAPI()
base_url = os.getenv('DAPR_HTTP_ENDPOINT', 'http://localhost')
package_db = os.getenv('DAPR_PACKAGES_DB', 'packagesdb')
pubsub_name = os.getenv('DAPR_PUB_SUB', 'aws-pubsub')
target_app_id = os.getenv('DAPR_TARGET_APP_ID', '')
target_api_token = os.getenv('DAPR_TARGET_API_TOKEN', '')
logging.basicConfig(level=logging.INFO)





@app.post('/api/pickup')
async def pick_package_event(event: CloudEvent):
    with DaprClient() as d:
        logging.info(f'Received event: %s:' % {event.data['package_model']})
        print(f'Received event pickup: {event}')
        try:
            user_id: str = "8ecf99c5-99bf-465c-b144-e7d21f79cf3e"
            package_model = json.loads(event.data['package_model'])

            # assign package to available delivery guy.

            headers = {'dapr-app-id': target_app_id,'dapr-api-token': target_api_token,
                       'content-type': 'application/json'}
            try:
                result = requests.get(
                    url='%s/api/users/{}'.format(user_id) % base_url,
                    params=user_id,
                    headers=headers
                )

                if result.ok:
                    logging.info('Invocation successful with status code: %s' %
                                 result.status_code)
                    print("result is %s" % result.json())
                    driver_details = result.json()

                    package_model['deliveryAgentId'] = driver_details['id']

                    # send object back to be assigned

                    # AssignPackageEvent



                    # send event back to package-service.
                    # Package service saves the item and then sends a notification. (ASSGINED)
                    # get all events assigned with delivery address = my address(i'm the delivery guy)

                    # start journey.(create delivery collection)
                    # send delivery status event to package. update in transaction.

                    return result.json()

                else:
                    logging.error(
                        'Error occurred while invoking App ID: %s' % result.reason)
                    raise HTTPException(status_code=500, detail=result.reason)

            except grpc.RpcError as err:
                logging.error(f"ErrorCode={err.code()}")
                raise HTTPException(status_code=500, detail=err.details())

            # update package record in kv store


        except grpc.RpcError as err:
            print(f"Error={err.details()}")
            raise HTTPException(status_code=500, detail=err.details())
