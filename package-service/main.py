import json
import os

from dapr.clients import DaprClient
from fastapi import FastAPI, HTTPException
from models.cloud_events import CloudEvent
import grpc

import logging
from models.package_model import PackageModel, PackageStatus

app = FastAPI()
package_db_with_outbox = os.getenv('DAPR_PACKAGES_DB_WITH_OUTBOX', '')
package_db_no_outbox = os.getenv('DAPR_PACKAGES_DB_NO_OUTBOX', '')
pubsub_name = os.getenv('DAPR_PUB_SUB', 'awssqs')
topic_name = os.getenv('DAPR_PACKAGE_PICKUP_TOPIC_NAME', 'package-pickup-request')
logging.basicConfig(level=logging.INFO)


@app.post('/v1.0/state/packages')
def create_package(package_model: PackageModel):
    with DaprClient() as d:
        print(f"package={package_model.model_dump()}")
        try:
            d.save_state(store_name=package_db_no_outbox,
                         key=str(package_model.id),
                         value=package_model.model_dump_json(),
                         state_metadata={"contentType": "application/json"})

            return package_model
        except grpc.RpcError as err:
            print(f"Error={err.details()}")
            raise HTTPException(status_code=500, detail=err.details())


@app.get('/v1.0/state/packages/{package_id}')
def get_package(package_id: str):
    with DaprClient() as d:
        try:
            kv = d.get_state(package_db_with_outbox, package_id)
            print(f"value of kv is {kv.data}")
            if kv.data:
                package_model = PackageModel(**json.loads(kv.data))

                return package_model.model_dump()
            else:
                return {
                    "status_code": 204,
                    "message": "package not found"}

        except grpc.RpcError as err:

            raise HTTPException(status_code=500, detail=err.details())


# Responds to ASSIGN_PACKAGE_REQUEST
@app.post('/v1.0/subscribe/packages/assign')
def assign_package_request(event: CloudEvent):
    with DaprClient() as d:
        logging.info(f'Received event: %s:' % {event.data['package_model']})
        try:
            package_model = json.loads(event.data['package_model'])
            d.save_state(store_name=package_db_no_outbox,
                         key=str(package_model['id']),
                         value=json.dumps(package_model),
                         state_metadata={"contentType": "application/json"})


        except grpc.RpcError as err:
            logging.error(f"ErrorCode={err.code()}")
            raise HTTPException(status_code=500, detail=err.details())


# RESPONDS TO DELIVERY STATUS UPDATE EVENT
@app.post('/v1.0/subscribe/packages/delivery-status')
def delivery_status_update(event: CloudEvent):
    with DaprClient() as d:
        logging.info(f'delivery status update event id: %s:' % event.data['id'])
        try:

            package_id = event.data['id']
            kv = d.get_state(package_db_with_outbox, package_id)
            package_model = PackageModel(**json.loads(kv.data))

            package_model.packageStatus = PackageStatus.IN_TRANSIT

            d.save_state(store_name=package_db_no_outbox,
                         key=str(package_model.id),
                         value=package_model.model_dump_json(),
                         state_metadata={"contentType": "application/json"})

            return {"message": "successfully updated package status"}


        except grpc.RpcError as err:
            logging.error(f"ErrorCode={err.code()}")
            raise HTTPException(status_code=500, detail=err.details())


@app.post('/v1.0/subscribe/packages/drop-off')
def package_drop_off_event(event: CloudEvent):
    with DaprClient() as d:
        logging.info(f'delivery status update event id: %s:' % event.data['id'])
        try:

            package_id = event.data['id']
            kv = d.get_state(package_db_no_outbox, package_id)
            package_model = PackageModel(**json.loads(kv.data))

            # update package status to delivered
            package_model.packageStatus = PackageStatus.DELIVERED

            d.save_state(store_name=package_db_no_outbox,
                         key=str(package_model.id),
                         value=package_model.model_dump_json(),
                         state_metadata={"contentType": "application/json"})

            return {"message": "package successfully updated"}


        except grpc.RpcError as err:
            logging.error(f"ErrorCode={err.code()}")
            raise HTTPException(status_code=500, detail=err.details())


@app.get('/v1.0/publish/packages/send/{package_id}')
def package_pickup_request(package_id: str):
    with DaprClient() as d:
        print(f"package_id={package_id}")

        try:
            # get complete package infor
            kv = d.get_state(package_db_with_outbox, package_id)
            package_model = PackageModel(**json.loads(kv.data))

            # update package status
            package_model.packageStatus = PackageStatus.PICK_UP_REQUEST

            # pacakge
            d.save_state(store_name=package_db_with_outbox,
                         key=str(package_model.id),
                         value=package_model.model_dump_json(),
                         state_metadata={"contentType": "application/json"})

            return {"message": "successful"}
        except grpc.RpcError as err:
            print(f"Error={err.details()}")
            raise HTTPException(status_code=500, detail=err.details())


@app.get('/v1.0/state/packages/users/{user_id}')
def get_all_user_packages(user_id: str):
    with DaprClient() as d:
        try:
            user_packages = []

            query_filter = json.dumps({
                "filter": {
                    "EQ": {"senderId": user_id}
                },
                "sort": [
                    {
                        "key": "id",
                        "order": "DESC"
                    }
                ]
            })

            kv = d.query_state(

                store_name=package_db_no_outbox,
                query=query_filter

            )
            print(f"packages are {kv}")

            for item in kv.results:
                package_model = PackageModel(**json.loads(item.value))
                user_packages.append(package_model)
                print(f"order is {package_model.model_dump()}")

            return user_packages
        except grpc.RpcError as err:
            print(f"Error={err.details()}")
            raise HTTPException(status_code=500, detail=err.details())
