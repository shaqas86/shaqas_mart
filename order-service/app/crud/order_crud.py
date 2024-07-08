from fastapi import HTTPException
from sqlmodel import Session,select
from app.models.order_model import OrderItem, OrderItemUpdate

# Add a New Order to the Database
def add_new_order(order_data: OrderItem, session: Session):
    session.add(order_data)
    session.commit()
    session.refresh(order_data)
    return order_data

# Get All Orders from the Database
def get_all_orders(session: Session):
    all_order = session.exec(select(OrderItem)).all()
    return all_order

# Get a Order by ID

def get_order_by_id(order_id:int, session:Session):
    order=session.exec(select(OrderItem).where(OrderItem.order_item_id== order_id)).one_or_none()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

def delete_order_by_id(order_item_id:int , session:Session):
    #Step:1 Get the Order by ID
    order=session.exec(select(OrderItem).where(OrderItem.order_item_id== order_item_id)).one_or_none()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    #step:2 Delete the Order
    session.delete(order)
    session.commit()
    return{"message": "Order Deleted Successfully"}

# Update Order by ID
def update_order_by_id(order_id:int,to_update_order_data:OrderItemUpdate,session:Session):
    #Step:1 Get the order by ID
    order=session.exec(select(OrderItem).where(OrderItem.order_item_id== order_id)).one_or_none()
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    #update the order
    order_data = to_update_order_data.model_dump(exclude_unset=True)
    order.sqlmodel_update(order_data)
    session.add(order)
    session.commit()
    return order
# Validate Product by ID
def validate_order_by_id(order_id: int, session: Session) -> OrderItem | None:
    order = session.exec(select(OrderItem).where(OrderItem.order_item_id == order_id)).one_or_none()
    return order
    
