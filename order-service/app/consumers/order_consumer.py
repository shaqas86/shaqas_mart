from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import json
from app.models.order_model import OrderItem
from app.crud.order_crud import validate_order_by_id,add_new_order
from app.deps import get_kafka_producer,get_session
from app.order_settings import KAFKA_CONSUMER_GROUP_ID_FOR_ORDER,KAFKA_ORDER_TOPIC

topic = KAFKA_ORDER_TOPIC
kafka_group= KAFKA_CONSUMER_GROUP_ID_FOR_ORDER


async def consume_order_messages(topic, bootstrap_servers):
    # Create a consumer instance.
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id= kafka_group,
        # auto_offset_reset="earliest",
    )
 
    await consumer.start()
    try:
        # Continuously listen for messages.
        async for message in consumer:
            print("RAW")
            print(f"Received message on topic {message.topic}")

            order_data = json.loads(message.value.decode())
            print("TYPE", (type(order_data)))
            print(f"Product Data {order_data}")

            with next(get_session()) as session:
                print("SAVING DATA TO DATABSE")
                db_insert_order = add_new_order(
                    order_data=OrderItem(**order_data), session=session)
                print("DB_INSERT_ORDER", db_insert_order)

            # Here you can add code to process each message.
            # Example: parse the message, store it in a database, etc.
    finally:
        # Ensure to close the consumer when done.
        await consumer.stop()
    # # Start the consumer.
    # await consumer.start()
    # try:
    #     # Continuously listen for messages.
    #     async for message in consumer:
    #         print("\n\n RAW ORDER MESSAGE\n\n ")
    #         print(f"Received message on topic {message.topic}")
    #         print(f"Message Value {message.value}")

    #         # 1. Extract Order Id
    #         order_data = json.loads(message.value.decode())
    #         order_id = order_data["order_id"]
    #         print("ORDER ID", order_id)

    #         # 2. Check if Order Id is Valid
    #         with next(get_session()) as session:
    #             order = validate_order_by_id(
    #                 order_id=order_id, session=session)
    #             print("ORDER VALIDATION CHECK", order)
    #             # 3. If Valid
    #             if order is not None:
    #                     # - Write New Topic
    #                 print("ORDER VALIDATION CHECK NOT NONE")
                    
    #                 producer = AIOKafkaProducer(
    #                     bootstrap_servers='broker:19092')
    #                 await producer.start()
    #                 try:
    #                     await producer.send_and_wait(
    #                         "order-add-response",
    #                         message.value
    #                     )
    #                 finally:
    #                     await producer.stop()

    #         # Here you can add code to process each message.
    #         # Example: parse the message, store it in a database, etc.
    # finally:
    #     # Ensure to close the consumer when done.
    #     await consumer.stop()