from app.models.schemas import(ConversationState,Entities,Intent,ConversationStep,)

#Manage Conversation state for each user
class StateManager:

    def __init__(self) -> None:
        self._states:dict[str,ConversationState] ={}

    #Get new state or create new state for user 
    def get_state(self,user_id:str) -> ConversationState:
        if user_id not in self._states:
            self._states[user_id] = ConversationState(user_id=user_id)
        return self._states[user_id]

    #Update user current intent 
    def update_intent(self,user_id: str,intent: Intent,) -> ConversationState:
        state = self.get_state(user_id)
        state.intent = intent
        return state 

    #Updated nexwly extracted entities 
    def update_entities(self,user_id: str,entities: Entities,) -> ConversationState:
        state = self.get_state(user_id)

        if entities.dish is not None:
            state.entities.dish = entities.dish

        if entities.category is not None:
            state.entities.category = entities.category

        if entities.quantity is not None:
            state.entities.quantity = entities.quantity

        if entities.address is not None:
            state.entities.address = entities.address

        if entities.order_id is not None:
            state.entities.order_id = entities.order_id

        if entities.confirmation is not None:
            state.entities.confirmation = entities.confirmation

        return state

    #Set the user current conversation step 
    def set_step(self,user_id: str,step: ConversationStep,) -> ConversationState:

        state=self.get_state(user_id)
        state.step=step
        return state 

    #Clear a user conversation state 
    def clear_state(self,user_id:str)->None:
        self._states.pop(user_id,None)



    
        