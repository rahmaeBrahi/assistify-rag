"""
Production RAG Service — LangChain + OpenRouter + FAISS
Replaces the local ML orchestrator with a cloud LLM + retrieval-augmented pipeline.

Design:
  1. Products are loaded from DB and embedded into an in-memory FAISS vector store.
  2. Per-conversation memory (window=10 turns) is kept in a module-level dict.
  3. Each user message triggers:
       • Language detection
       • FAISS similarity search over products
       • Prompt construction (system + retrieved context + history + message)
       • OpenRouter LLM call via LangChain
       • Structured response dict (preserves original API contract)
"""

from __future__ import annotations

import gc
import logging
import re
import threading
from typing import Any, Dict, List, Optional

from decouple import config

logger = logging.getLogger(__name__)

# ─── Config (from environment) ────────────────────────────────────────────────
OPENROUTER_API_KEY: str = config("OPENROUTER_API_KEY", default="")
OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
LLM_MODEL: str = config(
    "LLM_MODEL",
    default="openai/gpt-4o-mini",
)
EMBED_MODEL: str = config(
    "EMBED_MODEL",
    default="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
)
MAX_HISTORY_TURNS: int = int(config("MAX_HISTORY_TURNS", default=10))
RETRIEVAL_TOP_K: int = int(config("RETRIEVAL_TOP_K", default=5))
LLM_MAX_TOKENS: int = int(config("LLM_MAX_TOKENS", default=1024))
LLM_TEMPERATURE: float = float(config("LLM_TEMPERATURE", default=0.6))

# ─── Module-level singletons ──────────────────────────────────────────────────
_vector_store = None
_embeddings = None
_llm = None
_vs_lock = threading.Lock()
_conversation_histories: Dict[str, List[Dict[str, str]]] = {}

# ─── Regex ────────────────────────────────────────────────────────────────────
_RE_ARABIC = re.compile(r"[؀-ۿ]")
_RE_ORDER_NUM = re.compile(r"\bord-\d{4}-\d{1,5}\b", re.I)

# ─── System Prompt ────────────────────────────────────────────────────────────
_SYSTEM_PROMPT = """You are Assistify AI — the intelligent customer support assistant for a medical equipment e-commerce store in Egypt.

MISSION
• Help customers find the right medical products (blood pressure monitors, glucose monitors, oximeters, thermometers, nebulizers, heating pads, etc.)
• Handle order tracking, order placement assistance, complaints, and general inquiries
• Be warm, helpful, and professional
• Always respond in the SAME LANGUAGE the customer uses (Arabic or English)
• Keep responses concise but informative

CAPABILITIES
1. Product Discovery — recommend products based on customer needs, symptoms, or conditions
2. Product Details — explain features, prices (in EGP), benefits, and use cases
3. Order Support — help track orders (format: ORD-YYYY-#####), handle complaints
4. Purchase Guidance — walk customers through purchasing steps
5. Multilingual — Arabic (Egyptian dialect welcome) and English

PRODUCT CONTEXT
Use the RETRIEVED PRODUCTS section when answering product questions. Always mention:
• Product name and price in EGP
• Key features relevant to the customer's need
• Who it's suitable for

RULES
• If a customer asks about an order number, remind them to provide the order number in the format ORD-YYYY-#####
• For medical symptoms, recommend products gently but remind them to consult a doctor
• For complaints, acknowledge, apologize sincerely, and offer help
• Do NOT discuss topics outside the store scope (weather, politics, finance, etc.)
• Do NOT invent product details not in the context — say you'll check if unsure
• Keep responses under 300 words unless listing multiple products

TONE
• Warm and professional
• Use emojis sparingly but appropriately (🩺 💊 🛒 ✅)
• Egyptian Arabic customers: use friendly Egyptian dialect when appropriate
"""

# ─── Helpers ──────────────────────────────────────────────────────────────────

def _detect_language(message: str) -> str:
    return "ar" if _RE_ARABIC.search(message) else "en"


def _detect_intent(message: str, language: str) -> str:
    """Light intent detection without ML — used for metadata only."""
    tl = message.lower()
    if _RE_ORDER_NUM.search(tl) or any(k in tl for k in ["track", "order status", "فين طلبي", "تتبع"]):
        return "order_tracking"
    if any(k in tl for k in ["شراء", "اطلب", "buy", "order", "purchase"]):
        return "purchase_intent"
    if any(k in tl for k in ["شكوى", "complaint", "مشكلة", "تلف", "مكسور"]):
        return "complaint"
    if any(k in tl for k in ["سعر", "price", "بكام", "how much"]):
        return "price_inquiry"
    if any(k in tl for k in ["مرحب", "hello", "hi", "السلام"]):
        return "greeting"
    if any(k in tl for k in ["وداع", "bye", "goodbye", "شكرا"]):
        return "goodbye"
    return "inquiry"


def _get_embeddings():
    global _embeddings
    if _embeddings is None:
        try:
            from langchain_community.embeddings import HuggingFaceEmbeddings
            _embeddings = HuggingFaceEmbeddings(
                model_name=EMBED_MODEL,
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True},
            )
            logger.info("Embeddings model loaded: %s", EMBED_MODEL)
        except Exception as exc:
            logger.error("Failed to load embeddings: %s", exc)
            _embeddings = None
    return _embeddings


def _get_llm():
    global _llm
    if _llm is None:
        if not OPENROUTER_API_KEY:
            logger.warning("OPENROUTER_API_KEY not set — LLM unavailable")
            return None
        try:
            from langchain_openai import ChatOpenAI
            _llm = ChatOpenAI(
                model=LLM_MODEL,
                openai_api_key=OPENROUTER_API_KEY,
                openai_api_base=OPENROUTER_BASE_URL,
                max_tokens=LLM_MAX_TOKENS,
                temperature=LLM_TEMPERATURE,
                request_timeout=30,
                default_headers={
                    "HTTP-Referer": "https://assistify.ai",
                    "X-Title": "Assistify AI",
                },
            )
            logger.info("LLM ready: %s via OpenRouter", LLM_MODEL)
        except Exception as exc:
            logger.error("Failed to init LLM: %s", exc)
            _llm = None
    return _llm


def _build_product_documents(products: List[Dict]) -> List[Any]:
    """Convert product dicts to LangChain Documents."""
    from langchain_core.documents import Document

    docs = []
    for p in products:
        features = p.get("features") or []
        suitable = p.get("suitable_for") or []
        use_cases = p.get("use_cases") or []

        # Arabic name/description fallback
        name = p.get("name") or p.get("title") or "Product"
        description = p.get("description") or ""
        price = p.get("price") or ""
        currency = p.get("currency") or "EGP"
        product_id = p.get("id")

        content = (
            f"Product: {name}\n"
            f"Price: {price} {currency}\n"
            f"Description: {description}\n"
        )
        if features:
            content += f"Features: {', '.join(str(f) for f in features)}\n"
        if suitable:
            content += f"Suitable for: {', '.join(str(s) for s in suitable)}\n"
        if use_cases:
            content += f"Use cases: {', '.join(str(u) for u in use_cases)}\n"

        docs.append(
            Document(
                page_content=content,
                metadata={"product_id": product_id, "name": name, "price": str(price)},
            )
        )
    return docs


def build_vector_store(products: Optional[List[Dict]] = None) -> bool:
    """Build (or rebuild) the FAISS vector store from products.
    Called on app startup or when product catalog changes.
    """
    global _vector_store
    with _vs_lock:
        try:
            if products is None:
                products = _fetch_products_from_db()

            if not products:
                logger.warning("No products found — vector store not built")
                return False

            emb = _get_embeddings()
            if emb is None:
                return False

            from langchain_community.vectorstores import FAISS

            docs = _build_product_documents(products)
            _vector_store = FAISS.from_documents(docs, emb)
            logger.info("Vector store built with %d product documents", len(docs))
            return True
        except Exception as exc:
            logger.error("Failed to build vector store: %s", exc, exc_info=True)
            return False


def _fetch_products_from_db() -> List[Dict]:
    """Fetch all active products from the Django DB."""
    try:
        from assistify.apps.products.models import Product

        qs = Product.objects.filter(is_active=True).prefetch_related(
            "benefits"
        )
        products = []
        for p in qs:
            products.append(
                {
                    "id": p.id,
                    "name": p.name,
                    "description": p.description,
                    "price": str(p.price),
                    "currency": p.currency,
                    "features": p.features or [],
                    "suitable_for": p.suitable_for or [],
                    "use_cases": p.use_cases or [],
                }
            )
        return products
    except Exception as exc:
        logger.error("DB product fetch failed: %s", exc)
        return []


def _get_vector_store():
    """Lazy-init: build vector store on first request if not yet built."""
    global _vector_store
    if _vector_store is None:
        with _vs_lock:
            if _vector_store is None:
                build_vector_store()
    return _vector_store


def _retrieve_context(message: str) -> str:
    """Retrieve relevant product context for the user message."""
    try:
        vs = _get_vector_store()
        if vs is None:
            return ""
        docs = vs.similarity_search(message, k=RETRIEVAL_TOP_K)
        if not docs:
            return ""
        context = "\n\n".join(d.page_content for d in docs)
        return f"RETRIEVED PRODUCTS:\n{context}"
    except Exception as exc:
        logger.error("Retrieval error: %s", exc)
        return ""


def _get_history(conversation_id: Optional[int]) -> List[Dict[str, str]]:
    key = str(conversation_id) if conversation_id else "anon"
    return _conversation_histories.get(key, [])


def _update_history(
    conversation_id: Optional[int], user_msg: str, assistant_msg: str
) -> None:
    key = str(conversation_id) if conversation_id else "anon"
    history = _conversation_histories.setdefault(key, [])
    history.append({"role": "user", "content": user_msg})
    history.append({"role": "assistant", "content": assistant_msg})
    # Keep window
    if len(history) > MAX_HISTORY_TURNS * 2:
        _conversation_histories[key] = history[-(MAX_HISTORY_TURNS * 2):]


def _build_messages(
    message: str, context: str, history: List[Dict[str, str]]
) -> List[Any]:
    """Build the message list for the LLM call."""
    from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

    msgs: List[Any] = [SystemMessage(content=_SYSTEM_PROMPT)]

    # Inject retrieved context as a system note
    if context:
        msgs.append(SystemMessage(content=context))

    # Conversation history
    for turn in history:
        if turn["role"] == "user":
            msgs.append(HumanMessage(content=turn["content"]))
        else:
            msgs.append(AIMessage(content=turn["content"]))

    # Current user message
    msgs.append(HumanMessage(content=message))
    return msgs


# ─── Public API ───────────────────────────────────────────────────────────────

def get_rag_response(
    message: str,
    user_id: Optional[int] = None,
    conversation_id: Optional[int] = None,
) -> Dict:
    """
    Main entry point. Returns a dict matching the existing API contract:
    {
      "success": bool,
      "response": str,
      "intent": str,
      "sentiment": str,
      "recommendations": list,
      "confidence": {"intent": float, "sentiment": float},
      "metadata": {"recommendation_method": str, "user_name": None},
    }
    """
    language = _detect_language(message)
    intent = _detect_intent(message, language)

    llm = _get_llm()
    if llm is None:
        return _fallback_response(language)

    try:
        context = _retrieve_context(message)
        history = _get_history(conversation_id)
        msgs = _build_messages(message, context, history)

        ai_response = llm.invoke(msgs)
        reply_text = ai_response.content.strip()

        # Clean up any stray model artifacts
        reply_text = re.sub(r"<\|im_(start|end)\|>.*?$", "", reply_text, flags=re.S).strip()

        _update_history(conversation_id, message, reply_text)

        # Extract product recommendations from context docs for metadata
        recommendations = _extract_recommendations_from_context(context)

        return {
            "success": True,
            "response": reply_text,
            "intent": intent,
            "sentiment": "neutral",
            "recommendations": recommendations,
            "confidence": {"intent": 0.85, "sentiment": 0.5},
            "metadata": {
                "recommendation_method": "rag" if context else "llm",
                "user_name": None,
                "model": LLM_MODEL,
                "language": language,
            },
        }

    except Exception as exc:
        logger.error("RAG pipeline error: %s", exc, exc_info=True)
        return _fallback_response(language)


def _extract_recommendations_from_context(context: str) -> List[Dict]:
    """Parse product mentions from retrieved context for the recommendations field."""
    if not context:
        return []
    recommendations = []
    lines = context.split("\n")
    current: Dict = {}
    for line in lines:
        if line.startswith("Product:"):
            if current.get("name"):
                recommendations.append(current)
            current = {"name": line.replace("Product:", "").strip()}
        elif line.startswith("Price:") and current:
            price_str = line.replace("Price:", "").strip()
            current["price"] = price_str
    if current.get("name"):
        recommendations.append(current)
    return recommendations[:3]


def _fallback_response(language: str) -> Dict:
    if language == "ar":
        text = (
            "أنا مساعد Assistify 😊 أقدر أساعدك في المنتجات، "
            "الطلبات، التتبع، أو الشكاوى. تحب أساعدك في إيه؟"
        )
    else:
        text = (
            "I'm Assistify AI 😊 I can help you with products, "
            "orders, tracking, or complaints. How can I help you today?"
        )
    return {
        "success": True,
        "response": text,
        "intent": "greeting",
        "sentiment": "neutral",
        "recommendations": [],
        "confidence": {"intent": 0.5, "sentiment": 0.5},
        "metadata": {"recommendation_method": "fallback", "user_name": None},
    }


def invalidate_vector_store() -> None:
    """Call this when products are updated to force a rebuild on next request."""
    global _vector_store
    with _vs_lock:
        _vector_store = None
        gc.collect()
    logger.info("Vector store invalidated — will rebuild on next request")


def clear_conversation(conversation_id: Optional[int]) -> None:
    """Remove conversation history for a given ID."""
    key = str(conversation_id) if conversation_id else "anon"
    _conversation_histories.pop(key, None)
