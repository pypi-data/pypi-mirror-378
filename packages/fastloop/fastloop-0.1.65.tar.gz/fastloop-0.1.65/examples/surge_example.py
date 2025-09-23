from fastloop import FastLoop
from fastloop.integrations.surge import (
    SurgeIntegration,
    SurgeRxMessageEvent,
    SurgeTxMessageEvent,
)
from fastloop.loop import LoopState


async def handle_surge_events(event_data):
    event_type = event_data.get("type")

    if event_type == "surge_rx_message":
        rx_event = SurgeRxMessageEvent(**event_data)
        print(f"Received message from {rx_event.contact_first_name}: {rx_event.body}")

        reply = SurgeTxMessageEvent(
            body=f"Hello {rx_event.contact_first_name}! Thanks for your message.",
            first_name=rx_event.contact_first_name,
            last_name=rx_event.contact_last_name,
            phone_number=rx_event.contact_phone_number,
        )

        return LoopState(loop_id=rx_event.loop_id, data={"reply": reply})

    return LoopState()


async def main():
    surge_integration = SurgeIntegration(
        token="sk_demo_vu44wof4xp4g7hudwhifrjd2agmxft656j4crhu3fleg5pw7voa7f5xf",
        account_id="acct_01k5sczqfnfkns7gwr62k1avcv",
    )

    fastloop = FastLoop()
    fastloop.add_integration(surge_integration, "surge_loop")
    fastloop.add_loop("surge_loop", handle_surge_events)

    # Example of sending a message
    message_event = SurgeTxMessageEvent(
        body="Hello, world!",
        first_name="Luke",
        last_name="Lombardi",
        phone_number="+17184145662",
    )

    await surge_integration.emit(message_event)
    print("Message sent!")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
