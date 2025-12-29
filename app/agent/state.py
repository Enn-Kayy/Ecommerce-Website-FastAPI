from typing import TypedDict, Optional, Any

class AgentState(TypedDict):
    user_query: str
    user: Any

    product_name: Optional[str]
    requested_qty: Optional[int]

    product_id: Optional[int]
    available_stock: Optional[int]
    final_qty: Optional[int]

    response: Optional[str]
