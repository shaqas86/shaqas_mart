# # main.py
from contextlib import asynccontextmanager
# import select
from typing import Annotated
from sqlmodel import Session, SQLModel,select
from fastapi import FastAPI, Depends, HTTPException
from typing import AsyncGenerator
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import asyncio
import json

from app import order_settings
from app.order_settings import KAFKA_ORDER_TOPIC,BOOTSTRAP_SERVER
from app.db_engine import engine
from app.models.order_model import OrderItem,OrderItemUpdate
from app.crud.order_crud import add_new_order, get_all_orders, get_order_by_id, delete_order_by_id,update_order_by_id
from app.deps import get_session,get_kafka_producer
from app.consumers.order_consumer import consume_order_messages

topic= KAFKA_ORDER_TOPIC
bootstrap_server= BOOTSTRAP_SERVER

def create_db_and_tables() -> None:

    SQLModel.metadata.create_all(engine)


# The first part of the function, before the yield, will
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    print("Creating .... ?? !")

    task = asyncio.create_task(consume_order_messages(
        topic, bootstrap_server))
    # task=asyncio.create_task(consume_order_messages(
    #     "AddOrder",
    #     'broker:19092'
    # ))

    create_db_and_tables()
    yield


app = FastAPI(
    lifespan=lifespan,
    title="Hello World API with DB",
    version="0.0.1",
)


@app.get("/")
def read_root():
    return {"Hello": "Order Service"}


@app.post("/create-order/", response_model=OrderItem)
async def create_new_order(order: OrderItem, session: Annotated[Session, Depends(get_session)], producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]):
    """ Create a new order and send it to Kafka"""
    
    order_dict = {field: getattr(order, field) for field in order.dict()}
    order_json = json.dumps(order_dict).encode("utf-8")
    print("Order_JSON:", order_json)
    # Produce message
    await producer.send_and_wait(order_settings.KAFKA_ORDER_TOPIC, order_json)
    # new_product = add_new_product(product, session)
    return order

@app.get("/manage-orders/all", response_model=list[OrderItem])
def call_all_orders(session: Annotated[Session, Depends(get_session)]):
    """ Get all orders from the database"""
    return get_all_orders(session)
# @app.get("/manage-orders/all", response_model=list[OrderItem])
# def call_all_orders(session: Annotated[Session, Depends(get_session)],producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]):
#     """ Get all orders from the database"""
#     statement = select(OrderItem)
#     results = session.exec(statement)
#     print("results",results)
#     return results.all()

@app.get("/manage-orders/{order_item_id}", response_model=OrderItem)
def get_single_order(order_item_id: int, session: Annotated[Session, Depends(get_session)]):
    """ Get a single Order by ID"""
    try:
        return get_order_by_id(order_id= order_item_id, session=session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/manage-orders/{order_item_id}", response_model=dict)
def delete_single_order(order_item_id: int, session: Annotated[Session, Depends(get_session)]):
    
    
    """ Delete a single order by ID"""
    try:
        return delete_order_by_id(order_item_id=order_item_id, session=session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.patch("/manage-orders/{order_item_id}", response_model=OrderItem)
def update_single_order(order_item_id: int, order_update: OrderItemUpdate, session: Annotated[Session, Depends(get_session)]):
    """ Update a single order by ID"""
    try:
        return update_order_by_id(order_id=order_item_id, to_update_order_data=order_update, session=session)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# from contextlib import asynccontextmanager
# from typing import Annotated
# from sqlmodel import Session, SQLModel, select
# from fastapi import FastAPI, Depends, HTTPException
# from typing import AsyncGenerator
# from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
# import asyncio
# import json

# from app import settings
# from app.db_engine import engine
# from app.models.order_model import OrderItem
# from app.crud.order_crud import add_new_order, get_order_by_id, delete_order_by_id
# from app.deps import get_session
# from app.producer.producer import get_kafka_producer
# # from app.consumers.product_consumer import consume_messages
# from app.consumers.order_consumer import consume_order_messages

# def create_db_and_tables() -> None:
#     SQLModel.metadata.create_all(engine)

# @asynccontextmanager
# async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
#     print("Creating ... ?? !!!")

#     task = asyncio.create_task(consume_order_messages(
#         "AddOrder",
#         'broker:19092'
#     ))

#     create_db_and_tables()
#     yield

# app = FastAPI(
#     lifespan=lifespan,
#     title="Hello World API with DB",
#     version="0.0.1",
# )

# @app.get("/")
# def read_root():
#     return {"Hello": "Order Service"}

# @app.post("/create-order/", response_model=OrderItem)
# async def create_new_order(order: OrderItem, session: Annotated[Session, Depends(get_session)], producer: Annotated[AIOKafkaProducer, Depends(get_kafka_producer)]):
#     """ Create a new order and send it to Kafka"""
    
#     order_dict = {field: getattr(order, field) for field in order.dict()}
#     order_json = json.dumps(order_dict).encode("utf-8")
#     print("Order_JSON:", order_json)
#     # Produce message
#     await producer.send_and_wait(settings.KAFKA_ORDER_TOPIC, order_json)
#     return order

# @app.get("/manage-orders/all", response_model=list[OrderItem])
# def call_all_orders(session: Annotated[Session, Depends(get_session)]):
#     """ Get all orders from the database"""
#     statement = select(OrderItem)
#     results = session.exec(statement)
#     return results.all()

# @app.get("/manage-orders/{order_item_id}", response_model=OrderItem)
# def get_single_order(order_item_id: int, session: Annotated[Session, Depends(get_session)]):
#     """ Get a single Order by ID"""
#     try:
#         return get_order_by_id(OrderItem.order_item_id== order_item_id, session=session)
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @app.delete("/manage-orders/{order_item_id}", response_model=dict)
# def delete_single_order(order_item_id: int, session: Annotated[Session, Depends(get_session)]):
#     """ Delete a single order by ID"""
#     try:
#         return delete_order_by_id(order_item_id=OrderItem, session=session)
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

