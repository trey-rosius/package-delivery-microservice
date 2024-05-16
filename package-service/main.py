import json
import os

from dapr.clients import DaprClient
from fastapi import FastAPI, HTTPException
from models.cloud_events import CloudEvent
import grpc

import logging
from models.package_model import PackageModel

app = FastAPI()
package_db = os.getenv('DAPR_PACKAGES_DB', 'packagesdb')
pubsub_name = os.getenv('DAPR_PUB_SUB', 'awssqs')
topic_name = os.getenv('DAPR_PACKAGE_PICKUP_TOPIC_NAME', 'package-pickup-request')
logging.basicConfig(level=logging.INFO)


@app.post('/api/packages')
def create_package(package_model: PackageModel):
    with DaprClient() as d:
        print(f"package={package_model.model_dump()}")
        try:
            d.save_state(store_name=package_db,
                         key=str(package_model.id),
                         value=package_model.model_dump_json())

            return {"message": "package successfully created"}
        except grpc.RpcError as err:
            print(f"Error={err.details()}")
            raise HTTPException(status_code=500, detail=err.details())


@app.get('/api/packages/{package_id}')
def assign_package(event:CloudEvent):
    with DaprClient() as d:
        print(f"package={event.model_dump()}")

@app.get('/api/packages/{package_id}')
def send_package_pickup_request(package_id: str):
    with DaprClient() as d:
        print(f"package_id={package_id}")

        try:
            # get complete package infor
            kv = d.get_state(package_db, package_id)
            package_model = PackageModel(**json.loads(kv.data))

            # update package status
            package_model.packageStatus = "pick-up-request"

            d.save_state(store_name=package_db,
                         key=str(package_model.id),
                         value=package_model.model_dump_json())

            # send package pickup request event
            package_details = {
                "package_model": package_model.model_dump_json(),
                "event_type": "pickupRequest"
            }

            d.publish_event(
                pubsub_name=pubsub_name,
                topic_name=topic_name,
                data=json.dumps(package_details),
                data_content_type='application/json',
            )
            return {"message": "successful"}
        except grpc.RpcError as err:
            print(f"Error={err.details()}")
            raise HTTPException(status_code=500, detail=err.details())


@app.get('/api/packages/{userId}')
def get_all_packages(userId: str):
    with DaprClient() as d:
        try:
            query_filter = json.dumps({
                "filter": {
                    "EQ": {"senderId": userId}
                },
                "sort": [
                    {
                        "key": "id",
                        "order": "DESC"
                    }
                ]
            })
            kv = d.query_state(
                package_db,
                query_filter

            )

            for item in kv.results:
                package_model = PackageModel(**json.loads(item.value))
                print(f"order is {package_model.model_dump()}")

            print(f"package list={kv.results}")

            return {"data": "successfull"}
        except grpc.RpcError as err:
            print(f"Error={err.details()}")
            raise HTTPException(status_code=500, detail=err.details())
