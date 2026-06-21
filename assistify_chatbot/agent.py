import os
import json
import logging
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from langchain.tools import tool
import requests
from contextvars import ContextVar

current_source = ContextVar("current_source", default="web")

from shopify_service import (
    get_shopify_products, search_shopify_products,
    create_shopify_draft_order, get_shopify_draft_order_status
)

logger = logging.getLogger(__name__)

@tool
def fetch_products(query: str = "") -> str:
    """Fetch or search for available medical products in the store. Use this when the user asks about products, prices, or wants to buy something. If query is empty, returns all products."""
    source = current_source.get()
    try:
        if source == "whatsapp":
            if query:
                products = search_shopify_products(query)
            else:
                products = get_shopify_products()
                
            if not products:
                return "No products found."
            
            res = []
            for p in products:
                res.append(f"Name: {p['name']} | Price: {p['price']} EGP | VariantID: {p['variant_id']} | Desc: {p['description'][:50]}")
            return "\n".join(res[:10])
        else:
            backend_url = os.getenv("BACKEND_URL", "https://assistify-system-kuw2.vercel.app")
            url = f"{backend_url}/api/v1/products/"
            if query:
                url += f"?search={query}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            products = response.json()
            
            if not products:
                return "No products found."
                
            res = []
            for p in products:
                res.append(f"Name: {p.get('name')} | Price: {p.get('price')} {p.get('currency', 'EGP')} | VariantID: {p.get('id')} | Desc: {p.get('description', '')[:50]}")
            return "\n".join(res[:10])
    except Exception as e:
        logger.error(f"Error fetching products: {e}")
        return "Failed to fetch products."

@tool
def create_order(items_json: str, customer_name: str, phone: str, address: str, email: str = "", payment_method: str = "cod") -> str:
    """Create a new order for a customer. 
    You MUST collect ALL these details from the user before calling this tool: items_json (a valid JSON string representing a list of items, e.g. a JSON array of objects, where each object has variant_id and quantity keys), customer_name, phone, address. Email and payment_method are optional. payment_method MUST be 'cod' or 'card'."""
    source = current_source.get()
    try:
        try:
            items = json.loads(items_json)
        except json.JSONDecodeError:
            return "Error: items_json must be a valid JSON string representing a list of items."
            
        if not isinstance(items, list) or len(items) == 0:
            return "Error: items_json must contain at least one item."

        if payment_method not in ["cod", "card"]:
            payment_method = "cod"
            
        if source == "whatsapp":
            result = create_shopify_draft_order(items, customer_name, phone, address, email)
            return f"Order created successfully! Order Name: {result['draft_order_name']}, Payment Link: {result['invoice_url']}"
        else:
            backend_url = os.getenv("BACKEND_URL", "https://assistify-system-kuw2.vercel.app")
            url = f"{backend_url}/api/v1/orders/"
            backend_items = []
            for item in items:
                v_id = item.get("variant_id") or item.get("product_id")
                qty = item.get("quantity", 1)
                if isinstance(v_id, str) and "gid://" in v_id:
                    v_id = v_id.split("/")[-1]
                backend_items.append({"product_id": int(v_id), "quantity": int(qty)})

            payload = {
                "customer_email": email or f"{phone}@assistify.local",
                "payment_method": payment_method,
                "delivery_address": address,
                "phone": phone,
                "items": backend_items
            }
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code != 201:
                return f"Error from server: {response.text}"
            response.raise_for_status()
            result = response.json().get("order", {})
            return f"Order created successfully! Order Number: {result.get('order_number')}, Status: {result.get('status')}"
    except Exception as e:
        logger.error(f"Error creating order: {e}")
        return f"Error creating order: {str(e)}"

@tool
def track_order(order_id: str) -> str:
    """Track the status of an order by its ID or Number."""
    source = current_source.get()
    try:
        if source == "whatsapp":
            status = get_shopify_draft_order_status(order_id)
            if status:
                return f"Order Name: {status['name']}, Status: {status['status']}, Payment Link: {status['invoiceUrl']}"
            return "Order not found."
        else:
            backend_url = os.getenv("BACKEND_URL", "https://assistify-system-kuw2.vercel.app")
            url = f"{backend_url}/api/v1/orders/{order_id}/"
            response = requests.get(url, timeout=10)
            if response.status_code == 404:
                return "Order not found."
            response.raise_for_status()
            result = response.json()
            return f"Order Number: {result.get('order_number')}, Status: {result.get('status')}, Tracking URL: {result.get('tracking_url', 'Not available yet')}"
    except Exception as e:
        logger.error(f"Error tracking order: {e}")
        return f"Error tracking order: {str(e)}"

class ChatbotAgent:
    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY", "")
        if self.api_key:
            os.environ["OPENAI_API_KEY"] = self.api_key
            
        self.model_name = os.getenv("OPENROUTER_MODEL", "google/gemini-2.5-flash")
        self.llm = ChatOpenAI(
            model=self.model_name,
            base_url="https://openrouter.ai/api/v1",
            temperature=0.3,
            max_tokens=1024
        )
        self.tools = [fetch_products, create_order, track_order]
        self.memory_store = {}

    def _get_agent(self, session_id: str):
        if session_id not in self.memory_store:
            self.memory_store[session_id] = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
            
        from langchain.prompts import MessagesPlaceholder
        agent_kwargs = {
            "memory_prompts": [MessagesPlaceholder(variable_name="chat_history")]
        }
            
        return initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
            memory=self.memory_store[session_id],
            agent_kwargs=agent_kwargs,
            verbose=True,
            handle_parsing_errors=True
        )

    def process_message(self, message: str, session_id: str, source: str = "web") -> dict:
        if not message.strip():
            return {"success": False, "error": "Empty message"}
            
        current_source.set(source)
        agent = self._get_agent(session_id)
        
        system_prompt = (
            "You are Assistify, a friendly AI assistant for a medical supplies store in Egypt. "
            "Speak ONLY in natural Egyptian Arabic (اللهجة المصرية العامية) unless the user speaks English. "
            "Be friendly, natural, and concise like a real customer service agent. "
            "You can help users browse products, create orders, and track orders. "
            "If a user wants to order, politely ask for their Name, Phone, Address, and Quantity BEFORE using the create_order tool. "
            "IMPORTANT: When searching for products using fetch_products, use SHORT keywords (e.g. 'دعامة' instead of 'دعامة ركبة طبية بمفصلات') to get better results. "
            "CRITICAL: When you find a product the user wants, MEMORIZE its VariantID secretly so you can pass it to create_order later without having to search for it again."
        )
        
        try:
            full_prompt = f"{system_prompt}\nUser: {message}"
            response = agent.run(full_prompt)
            
            intent = "inquiry"
            sentiment = "neutral"
            recommendations = []
            confidence = {"intent": 0.85, "sentiment": 0.85}
            
            try:
                analysis_prompt = f"""
                Analyze the following conversation between a user and an AI assistant.
                User: {message}
                AI: {response}
                
                You must perform a strict probabilistic classification.
                Return a JSON object with exactly these keys:
                - "intent_probabilities": A dictionary mapping ALL these exact keys ("inquiry", "order_created", "order_tracking", "product_search", "complaint", "greeting") to a float probability between 0.0 and 1.0. The values MUST sum to exactly 1.0.
                - "sentiment_probabilities": A dictionary mapping ALL these exact keys ("positive", "neutral", "negative") to a float probability between 0.0 and 1.0. The values MUST sum to exactly 1.0.
                - "recommendations": A list of 1 to 3 related medical product names that would be logical recommendations based on the user's intent. Return an empty list if not applicable.
                
                Return ONLY the JSON. Do not include markdown code blocks.
                """
                from langchain_core.messages import HumanMessage
                analysis_response = self.llm.invoke([HumanMessage(content=analysis_prompt)])
                analysis_content = analysis_response.content.strip()
                
                # Extract JSON using substring to avoid markdown/text wrap issues
                start_idx = analysis_content.find('{')
                end_idx = analysis_content.rfind('}')
                if start_idx != -1 and end_idx != -1:
                    analysis_content = analysis_content[start_idx:end_idx+1]
                    
                analysis_data = json.loads(analysis_content)
                
                intent_probs = analysis_data.get("intent_probabilities", {"inquiry": 1.0})
                sentiment_probs = analysis_data.get("sentiment_probabilities", {"neutral": 1.0})
                
                # Calculate the maximum probability and its corresponding label
                best_intent = max(intent_probs.items(), key=lambda x: x[1])
                best_sentiment = max(sentiment_probs.items(), key=lambda x: x[1])
                
                intent = best_intent[0]
                sentiment = best_sentiment[0]
                
                # Use the probability of the predicted class as the confidence score
                # This is standard in ML (Softmax confidence) and much more stable than entropy
                confidence = {
                    "intent": round(best_intent[1], 2),
                    "sentiment": round(best_sentiment[1], 2)
                }
                recommendations = analysis_data.get("recommendations", recommendations)
            except Exception as e:
                logger.error(f"Error analyzing conversation probabilities: {e}")

            return {
                "success": True,
                "response": response,
                "intent": intent,
                "sentiment": sentiment,
                "recommendations": recommendations,
                "confidence": confidence,
                "metadata": {
                    "session_id": session_id
                }
            }
        except Exception as e:
            logger.error(f"LangChain agent error: {e}", exc_info=True)
            return {
                "success": False,
                "response": "عذراً، حدث خطأ أثناء معالجة طلبك. الرجاء المحاولة لاحقاً.",
                "error": str(e)
            }
