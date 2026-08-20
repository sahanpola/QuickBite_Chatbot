from dataclasses import dataclass,field
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


#Add All Current Converstation state 

class ConversationStep(str,Enum): 
    START ="start"
    AWAITING_DISH = "awaiting_dish"
    AWAITING_QUANTITY = "awaiting_quantity"
    AWAITING_ADDRESS = "awaiting_address"
    AWAITING_CONFIRMATION = "awaiting_confirmation"

    AWAITING_ORDER_ID = "awaiting_order_id"
    AWAITING_CANCELLATION_CONFIRMATION = (
        "awaiting_cancellation_confirmation"
    )

    COMPLETED = "completed"




#Strore the current state of a user's conversation 
@dataclass
class ConversationState:
    user_id:str 
    intent:Intent=Intent.UNKNOWN 
    step: ConversationStep = ConversationStep.START
    entities: Entities = field(default_factory=Entities)


#Available application routes.
class Route(str, Enum):
    

    ORDER = "order"
    TRACK = "track"
    CANCEL = "cancel"
    HELP = "help"
    GREETING = "greeting"
    FALLBACK = "fallback"