from typing import Optional,List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

class OrderItem(SQLModel, table=True):
       
    order_item_id: int|None = Field(default=None, primary_key=True)
    product_id: int
    quantity: int
    unit_price: float
    user_id: int
    user_email:str
    user_name:str
    product_name:str
    
# class Order(SQLModel, table=True):
       
#     order_id: int|None = Field(default=None, primary_key=True)
#     customer_id: int
#     order_date: datetime = Field(default_factory=datetime.utcnow)
#     total_amount: float
#     order_status: str

# #     items: List[OrderItem] = Relationship(back_populates="order")

# # OrderItem.order = Relationship(back_populates="items")