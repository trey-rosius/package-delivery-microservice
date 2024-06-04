from dapr.clients import DaprClient
def create_intent():
    print(f'create payment intent: Received input: {activity_input}.')
    payment_intent = client.payment_intents.create(
        params={
            "amount": activity_input.amount,
            "currency": "usd"

        }

    )
    return activities.reserve.flight(activity_input)