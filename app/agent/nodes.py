from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from app.agent.tools import get_product_by_name, place_order

def extract_entities(state, llm):
    prompt = PromptTemplate.from_template("""
    Extract the core product name and quantity from the user's request.
    Return ONLY a raw JSON strictly. Do NOT include any markdown formatting (like ```json), explanations, or additional text.

    Examples:
    "buy a gaming laptop" -> {{"product_name": "Laptop", "quantity": 1}}
    "get me 2 footballs" -> {{"product_name": "Football", "quantity": 2}}

    Request: "{query}"
    
    JSON:
    """)

    from langchain_core.output_parsers import StrOutputParser
    import json
    import re

    chain = prompt | llm | StrOutputParser()
    raw_response = chain.invoke({"query": state["user_query"]})
    
    # Clean response (remove markdown code blocks if any)
    cleaned = re.sub(r"```json|```", "", raw_response).strip()
    
    try:
        # try finding the first { and last }
        start = cleaned.find("{")
        end = cleaned.rfind("}") + 1
        if start != -1 and end != -1:
             cleaned = cleaned[start:end]
        
        data = json.loads(cleaned)
    except Exception:
        # Fallback default if parsing fails completely
        data = {"product_name": state["user_query"], "quantity": 1}

    state["product_name"] = data.get("product_name", "Unknown")
    state["requested_qty"] = data.get("quantity", 1)
    return state


def stock_and_order(state):
    product = get_product_by_name(state["product_name"])

    if not product:
        state["response"] = "❌ This product is not available on this platform."
        return state

    if product.stock_qty == 0:
        state["response"] = "❌ This product is out of stock."
        return state

    requested = state["requested_qty"]

    if requested > product.stock_qty:
        final_qty = product.stock_qty
        state["response"] = (
            f"⚠️ Only {product.stock_qty} items were available. "
            f"I have ordered {product.stock_qty} for you."
        )
    else:
        final_qty = requested
    
    user = state.get("user")
    if not user:
        state["response"] = "⚠️ You must be logged in to place an order."
        return state

    result = place_order(user, product.id, final_qty)
    
    if "error" in result:
         state["response"] = f"❌ Could not place order: {result['error']}"
    else:
         state["response"] = f"✅ Order placed successfully! Order ID: {result.get('order_id')}"

    state["product_id"] = product.id
    state["available_stock"] = product.stock_qty
    state["final_qty"] = final_qty

    return state
