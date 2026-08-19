from dataclasses import dataclass
from enum import Enum 
from typing import Optional 

#Customer Intent
class Intent(str,Enum):

    ORDER_FOOD = "order_food"  #Customer order food
    TRACK_ORDER = "track_order" #Customer want track order
    CANCEL_ORDER = "cancel_order" #Cancel ordr 
    HELP = "help" #Customer need help
    GREETING = "greeting" #Customer greeting
    UNKNOWN = "unknown"  #Cannot identify customer request 

#Entity Extract From Customer Message
@dataclass 
class Entities:
    dish: Optional[str] = None
    quantity: Optional[int] = None
    address: Optional[str] = None
    order_id: Optional[str] = None
    confirmation: Optional[bool] = None

#Output of any NLP componenet 
@dataclass
class NLPResult : 
    intent: Intent
    entities: Entities 
    confidence: float=0.0 
    