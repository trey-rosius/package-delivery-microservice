import json
import os

from dapr.clients import DaprClient
from fastapi import FastAPI, HTTPException
import requests
import grpc

from datetime import timedelta
from stripe import StripeClient, StripeError
from models.payment_model import PaymentModel
import logging
from stripe import StripeClient
import dapr.ext.workflow as wf

app = FastAPI()
base_url = os.getenv('DAPR_HTTP_ENDPOINT', 'http://localhost')
pubsub_name = os.getenv('DAPR_PUB_SUB', '')
payments_db = os.getenv('DAPR_PAYMENTS_COLLECTION', '')
stripe_secret = os.getenv('STRIPE_SECRET_KEY', '')

logging.basicConfig(level=logging.INFO)

app = FastAPI()
client = StripeClient(stripe_secret)
logging.basicConfig(level=logging.INFO)
wfr = wf.WorkflowRuntime()
wf_client = wf.DaprWorkflowClient()
wfr.start()


@app.get('/v1.0/payments/{payment_intent}/confirm')
def confirm_payment_intent(payment_intent: str):
    with DaprClient as d:

        print(f'payment intent: Received input: {payment_intent}.')
        try:
            kv = d.get_state(payments_db, payment_intent);
            print(f"value of kv is {kv.data}")
            if kv.data:
                payment_model = PaymentModel(**json.loads(kv.data))
                try:
                    payment_confirmation = client.payment_intents.confirm(payment_intent,
                                                                          params={
                                                                              "payment_method": "pm_card_visa",
                                                                              "return_url": "https://www.example.com",
                                                                          }

                                                                          )
                    d.raise_workflow_event()
                    return {"status": payment_confirmation['status'],
                            }

                except StripeError as err:

                    raise HTTPException(status_code=500, detail=err.user_message)

        except grpc.RpcError as err:

            raise HTTPException(status_code=500, detail=err.details())





@app.get('/v1.0/payments/{payment_intent}/cancel')
def cancel_payment_intent(payment_intent: str):
    print(f'cancel payment intent: Received input: {payment_intent}.')
    try:
        payment_cancel = client.payment_intents.cancel(payment_intent

                                                       )
        return {"cancel": payment_cancel,

                }

    except StripeError as err:

        raise HTTPException(status_code=500, detail=err.user_message)


@app.post('/v1.0/payment')
def initiate_payment(payment: PaymentModel):
    instance_id = wf_client.schedule_new_workflow(workflow=payment_workflow, input=payment)

    wf_client.wait_for_workflow_completion(instance_id)
    return "success"


@wfr.workflow(name='makePayment')
def payment_workflow(ctx: wf.DaprWorkflowContext, wf_input: PaymentModel):
    try:
        wf_input.instance_id = ctx.instance_id
        payment_intent_response = yield ctx.call_activity(create_payment_intent, input=wf_input)
        if payment_intent_response["status"] == "success":
            approval_task = ctx.wait_for_external_event("approve payment")
            timeout_event = ctx.create_timer(timedelta(seconds=200))
            winner = yield wf.when_any([approval_task, timeout_event])
            if winner == timeout_event:
                yield ctx.call_activity(send_notification_activity,
                                        input={
                                            "status": "failed",
                                            "message": f"Your payment with id {payment_intent_response['payment_intent_id']} timed out"
                                        })
                return
            approval_result = yield approval_task
            if approval_result["succeeded"]:
                yield ctx.call_activity(send_notification_activity,
                                        input={
                                            "status": "succeeded",
                                            "message": f"Your payment with id {payment_intent_response['payment_intent_id']} succeeded"
                                        })
            else:
                yield ctx.call_activity(send_notification_activity,
                                        input={
                                            "status": "Cancelled",
                                            "message": f"Your payment with id {payment_intent_response['payment_intent_id']} called"
                                        })


    except Exception as e:
        yield ctx.call_activity(error_handler, input=str(e))
        raise
    return [create_payment_intent, send_notification_activity, error_handler]


@wfr.activity
def error_handler(ctx, error):
    print(f'Executing error handler: {error}.')


@wfr.activity
def create_payment_intent(ctx, activity_input: PaymentModel):
    with DaprClient as d:
        try:
            print(f'create payment intent: Received input: {activity_input}.')
            payment_intent = client.payment_intents.create(
                params={
                    "amount": activity_input.amount,
                    "currency": "usd"

                }

            )
            activity_input.id = payment_intent.id
            activity_input.payment_intent_id = payment_intent.id
            d.save_state(store_name=payments_db,
                         key=activity_input.id,
                         value=activity_input.model_dump_json(),
                         state_metadata={"contentType": "application/json"})

            print(f'created payment intent: {activity_input}')

            return {
                "payment_intent_id": payment_intent.id,
                "status": "success"
            }
        except grpc.RpcError as err:
            print(f"Error={err.details()}")
            raise HTTPException(status_code=500, detail=err.details())





@wfr.activity
def send_notification_activity(ctx, activity_input):
    with DaprClient as d:
        '''
          d.publish_event(
            pubsub_name=pubsub_name,
            topic_name=topic_name,
            data=json.dumps(activity_input),
            data_content_type='application/json',
        )
        print(f"received notification activity: {activity_input}")
        return "success"
        '''
        print(f"received notification activity: {activity_input}")
