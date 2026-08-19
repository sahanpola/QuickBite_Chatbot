from typing import Any 

class MockBackend:

    #Show the menu and current order list
    def __init__(self) -> None:
        self.menu: dict[str,float]={

             "Margherita Pizza": 8.99,
            "Pepperoni Pizza": 10.49,
            "Veggie Supreme Pizza": 9.49,
            "Classic Cheeseburger": 7.99,
            "BBQ Bacon Burger": 9.99,
            "Caesar Salad": 6.49,
            "Grilled Chicken Wrap": 7.49,
            "Chocolate Lava Cake": 4.99,

        }

        self.orders: dict[str,dict[str,Any]]={}
        self._next_order_number = 1001

    # Return available menu and prices
    def get_menu(self)-> dict[str,float]:
        return self.menu.copy()

    #Create and Store New Order
    def create_order(

            self,
            dish:str,
            quantity:int,
            address: str,) -> dict[str,Any]:

        if dish not in self.menu:
            raise ValueError(f"'{dish}' is not available on the menu.")

        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero")

        order_id = f"QB-{self._next_order_number}"
        self._next_order_number +=1

        order = {
            "order_id": order_id,
            "dish": dish,
            "quantity": quantity,
            "address": address,
            "unit_price": self.menu[dish],
            "status": "preparing",

        }

        self.orders[order_id] = order

        return order.copy()

    #Return an order by ID, or None if it does not exist

    def get_order(self,order_id:str) -> dict[str,Any] | None:
        order=self.orders.get(order_id)
        return order.copy() if order else None 

    #Cancel the Order 

    def cancel_order(self,order_id:str)->bool:
        order = self.orders.get(order_id)

        if order is None:
            return False

        if order["status"]=="cancelled":
            return False

        order["status"] = "cancelled"
        return True

    




    

        

            
    

    